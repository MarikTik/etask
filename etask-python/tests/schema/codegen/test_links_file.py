# tools/tests/etask.schema/codegen/test_links_file.py
# SPDX-License-Identifier: MIT

import re

from etask.schema.tree import Tree
from etask.schema.codegen.emitter import Emitter
from etask.schema.codegen.links_file import LinksFile


def _render(tmp_path, text):
    """Builds a schema from `text` and renders links.hpp from it."""
    path = tmp_path / "schema.yaml"
    path.write_text(text)
    return LinksFile.render(Tree.build(path))


def _flat(out):
    """The output's prose as one line, so an assertion survives a line wrap.

    Strips the leading comment marker off each line first: a sentence wrapped
    across two comment lines is otherwise interrupted by a `*` no reader sees.
    """
    stripped = [re.sub(r"^\s*(\*/?|//)\s?", "", line) for line in out.splitlines()]
    return " ".join(" ".join(stripped).split())


def _need(out, namespace, direction):
    """The emitted `<direction>_payload_need` inside `namespace`."""
    body = out.split(f"namespace {namespace} {{")[1]
    match = re.search(
        rf"inline constexpr std::size_t {direction}_payload_need = (\d+);", body
    )
    assert match, f"no {direction}_payload_need in namespace {namespace}"
    return int(match.group(1))


# ----------------------------------------------------------------- one link


def test_one_link_emits_its_namespace_and_both_packets(tmp_path):
    out = _render(tmp_path,
        "system:\n"
        "  blink:\n    type: polled_task\n    params: { duty: uint8 }\n"
        "links:\n"
        "  serial:\n    transport: uart\n"
    )
    assert "namespace generated::links {" in out
    assert "namespace serial {" in out
    # Two packet types, not one: the directions are sized separately.
    assert "using request_packet_t = ecomm::protocol::packet<" in out
    assert "using reply_packet_t = ecomm::protocol::packet<" in out
    assert "inline constexpr bool any = true;" in out
    assert "DO NOT EDIT" in out


def test_link_policies_spell_the_ecomm_names(tmp_path):
    out = _render(tmp_path,
        "system:\n  blink:\n    type: polled_task\n"
        "links:\n  serial:\n    transport: uart\n"
    )
    # uart defaults: point_to_point, crc16, reliable -> sequenced.
    assert "ecomm::protocol::topology::point_to_point;" in out
    assert "using checksum_policy = ecomm::protocol::crc16;" in out
    assert "using sequence_policy = ecomm::protocol::sequenced;" in out


def test_tcp_link_defaults_to_no_checksum_and_no_sequence(tmp_path):
    out = _render(tmp_path,
        "system:\n  blink:\n    type: polled_task\n"
        "links:\n  net:\n    transport: tcp\n"
    )
    assert "using checksum_policy = ecomm::protocol::none;" in out
    assert "using sequence_policy = ecomm::protocol::no_sequence;" in out
    assert "ecomm::protocol::topology::network;" in out


def test_both_directions_share_one_header_type(tmp_path):
    out = _render(tmp_path,
        "system:\n  blink:\n    type: polled_task\n"
        "links:\n  serial:\n    transport: uart\n"
    )
    # One header alias, referenced by both packets - external_channel asserts it.
    assert out.count("using header_t = ecomm::protocol::packet_header<") == 1
    assert out.count("packet_size_for<request_payload_need, header_t>") == 1
    assert out.count("packet_size_for<reply_payload_need, header_t>") == 1


# -------------------------------------------------------------- many links


def test_several_links_each_get_a_namespace_in_declaration_order(tmp_path):
    out = _render(tmp_path,
        "system:\n  blink:\n    type: polled_task\n"
        "links:\n"
        "  serial:\n    transport: uart\n"
        "  net:\n    transport: tcp\n"
        "  radio:\n    transport: wifi\n"
    )
    for name in ("serial", "net", "radio"):
        assert f"namespace {name} {{" in out
        assert f"}} // namespace {name}" in out
    assert out.index("namespace serial {") < out.index("namespace net {")
    assert out.index("namespace net {") < out.index("namespace radio {")


def test_links_differ_in_policy_but_share_the_size_requirement(tmp_path):
    out = _render(tmp_path,
        "system:\n"
        "  blink:\n    type: polled_task\n    params: { duty: uint32 }\n"
        "links:\n"
        "  serial:\n    transport: uart\n"
        "  net:\n    transport: tcp\n"
    )
    # Any task may be asked for over any link, so the payload requirement is a
    # property of the task set, not of the link. The header differs; this does not.
    assert _need(out, "serial", "request") == _need(out, "net", "request")
    assert _need(out, "serial", "reply") == _need(out, "net", "reply")


# ------------------------------------------------------------ the two sizes


def test_the_two_directions_are_sized_independently(tmp_path):
    out = _render(tmp_path,
        "system:\n"
        "  cmd:\n    type: polled_task\n    params: { on: bool }\n"
        "  telemetry:\n    type: polled_task\n"
        "    returns: [double, double, double, uint64]\n"
        "links:\n  serial:\n    transport: uart\n"
    )
    # request: 1 directive + 1 uid + 1 param = 3; reply: 1 uid + 1 status + 32 = 34.
    assert _need(out, "serial", "request") == 3
    assert _need(out, "serial", "reply") == 34


def test_a_big_request_and_a_small_reply_invert_the_asymmetry(tmp_path):
    out = _render(tmp_path,
        "system:\n"
        "  load:\n    type: polled_task\n"
        "    params: { a: uint64, b: uint64, c: uint64 }\n"
        "    returns: [bool]\n"
        "links:\n  serial:\n    transport: uart\n"
    )
    assert _need(out, "serial", "request") == 1 + 1 + 24
    assert _need(out, "serial", "reply") == 1 + 1 + 1
    assert _need(out, "serial", "request") > _need(out, "serial", "reply")


def test_reply_is_sized_by_the_widest_shape_not_the_last(tmp_path):
    out = _render(tmp_path,
        "system:\n"
        "  probe:\n    type: polled_task\n"
        "    returns:\n"
        "      finished: [uint64, uint64]\n"
        "      task_io_error: [uint8]\n"
        "links:\n  serial:\n    transport: uart\n"
    )
    # Only one shape is ever on the wire at a time, but any of them may be.
    assert _need(out, "serial", "reply") == 1 + 1 + 16


def test_no_params_and_no_returns_leave_only_the_fixed_fields(tmp_path):
    out = _render(tmp_path,
        "system:\n  ping:\n    type: instant_task\n"
        "links:\n  serial:\n    transport: uart\n"
    )
    assert _need(out, "serial", "request") == 2   # directive + uid
    assert _need(out, "serial", "reply") == 2     # uid + status
    assert "No task takes parameters" in _flat(out)
    assert "No task returns anything" in _flat(out)


def test_uid_width_widens_both_directions(tmp_path):
    # Past 256 tasks the tree's uid becomes two bytes, and both directions spend
    # it: the request names the task, the reply names it back. Reached by task
    # count, which is the only thing that decides the width now that uids are
    # packed from zero rather than pinned.
    out = _render(tmp_path,
        "system:\n  bank:\n    type: abstract_scope\n"
        "    instances: [" + ", ".join(f"i{n}" for n in range(300)) + "]\n"
        "    children:\n      ping:\n        type: instant_task\n"
        "links:\n  serial:\n    transport: uart\n"
    )
    assert _need(out, "serial", "request") == 1 + 2
    assert _need(out, "serial", "reply") == 2 + 1
    assert "the 2-byte uid" in _flat(out)


# ---------------------------------------------------------------- rounding


def test_size_is_rounded_in_cpp_to_a_literal_eight(tmp_path):
    out = _render(tmp_path,
        "system:\n  blink:\n    type: polled_task\n"
        "links:\n  serial:\n    transport: uart\n"
    )
    # The rounding must be a literal 8. Rounding to sizeof(std::size_t) would give
    # the host (8) and an ESP32 (4) two different frame sizes from one schema.
    assert "((PayloadNeed + sizeof(Header)) / 8 + 1) * 8;" in out
    assert "sizeof(std::size_t)" not in out.split("*/")[-1]


def test_the_packet_size_is_never_a_python_computed_literal(tmp_path):
    out = _render(tmp_path,
        "system:\n  blink:\n    type: polled_task\n"
        "links:\n  serial:\n    transport: uart\n"
    )
    # Python cannot know sizeof(header_t) - it depends on the policies and on the
    # target - so the packet size must be an expression the compiler evaluates.
    body = out.split("using request_packet_t")[1].split(";")[0]
    assert "packet_size_for<" in body
    assert not re.search(r"packet<\s*\d+", body)


def test_rounding_formula_is_strictly_above_the_header():
    # The emitted expression, evaluated in Python for a range of header widths.
    def emitted(need, header):
        return ((need + header) // 8 + 1) * 8

    for header in range(0, 17):
        for need in range(1, 80):
            size = emitted(need, header)
            assert size % 8 == 0            # ecomm: word alignment, on any target
            assert size > header            # ecomm: at least one payload byte
            assert size - header >= need    # and it actually fits the payload


# --------------------------------------------------------- reliability


def test_reliable_link_emits_its_retry_constants(tmp_path):
    out = _render(tmp_path,
        "system:\n  blink:\n    type: polled_task\n"
        "links:\n"
        "  serial:\n    transport: uart\n    retries: 5\n    buffer_depth: 2\n"
    )
    assert "inline constexpr bool reliable = true;" in out
    assert "inline constexpr unsigned retries = 5;" in out
    assert "inline constexpr unsigned buffer_depth = 2;" in out


def test_reliable_defaults_are_emitted_when_unstated(tmp_path):
    out = _render(tmp_path,
        "system:\n  blink:\n    type: polled_task\n"
        "links:\n  serial:\n    transport: uart\n"
    )
    assert "inline constexpr unsigned retries = 3;" in out
    assert "inline constexpr unsigned buffer_depth = 4;" in out


def test_unreliable_link_emits_no_retry_constants(tmp_path):
    out = _render(tmp_path,
        "system:\n  blink:\n    type: polled_task\n"
        "links:\n  net:\n    transport: tcp\n"
    )
    assert "inline constexpr bool reliable = false;" in out
    # Nothing is ever resent, so a retry budget would be a number no code reads.
    assert "retries" not in out.split("namespace net {")[1].split("} // namespace net")[0].replace(
        "No `retries` or `buffer_depth` here", "")
    assert "inline constexpr unsigned buffer_depth" not in out


# ------------------------------------------------------- traceable comments


def test_the_driving_task_is_named_for_each_direction(tmp_path):
    out = _render(tmp_path,
        "system:\n"
        "  small:\n    type: polled_task\n    params: { a: uint8 }\n"
        "  wide:\n    type: polled_task\n"
        "    params: { a: uint64, b: uint64 }\n"
        "  chatty:\n    type: polled_task\n    returns: [double, double]\n"
        "links:\n  serial:\n    transport: uart\n"
    )
    # A surprising number must be traceable to the task that caused it.
    flat = _flat(out)
    assert "`wide` at 16 bytes" in flat
    assert "`chatty on task_finished` at 16 bytes" in flat
    assert "`small`" not in flat


def test_the_driving_task_names_its_scope_path(tmp_path):
    out = _render(tmp_path,
        "system:\n"
        "  motor:\n    type: scope\n    children:\n"
        "      spin:\n        type: polled_task\n"
        "        params: { rpm: uint32, ms: uint32 }\n"
        "links:\n  serial:\n    transport: uart\n"
    )
    assert "`motor.spin` at 8 bytes" in _flat(out)


def test_defaults_explain_themselves(tmp_path):
    out = _render(tmp_path,
        "system:\n  blink:\n    type: polled_task\n"
        "links:\n"
        "  serial:\n    transport: uart\n"
        "  net:\n    transport: tcp\n"
    )
    # A reader must not have to guess why their UART link got crc16.
    flat = _flat(out)
    assert "sixteen bits is the cheapest width" in flat
    assert "already checksums every byte it carries" in flat
    assert "already delivers every frame in order" in flat
    assert "exactly one peer" in flat


def test_an_explicit_checksum_says_it_was_declared(tmp_path):
    out = _render(tmp_path,
        "system:\n  blink:\n    type: polled_task\n"
        "links:\n  radio:\n    transport: wifi\n    checksum: crc32\n"
    )
    assert "the schema declared `checksum: crc32`" in _flat(out)
    assert "using checksum_policy = ecomm::protocol::crc32;" in out


# --------------------------------------------------------------- no links


def test_no_links_still_generates_a_wellformed_header(tmp_path):
    out = _render(tmp_path, "system:\n  blink:\n    type: polled_task\n")
    assert "#ifndef GENERATED_LINKS_HPP_" in out
    assert "namespace generated::links {" in out
    assert "inline constexpr bool any = false;" in out
    assert "#endif // GENERATED_LINKS_HPP_" in out


def test_no_links_pulls_in_no_ecomm_headers(tmp_path):
    out = _render(tmp_path, "system:\n  blink:\n    type: polled_task\n")
    # Nothing to instantiate, so nothing to include: a project with no external
    # link must not acquire a dependency on ecomm by generating cleanly.
    assert "ecomm/" not in out
    assert "packet_size_for" not in out
    assert "namespace serial" not in out


# ------------------------------------------------------------- the emitter


def test_emitter_writes_links_when_the_path_is_given(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text(
        "system:\n  blink:\n    type: polled_task\n"
        "links:\n  serial:\n    transport: uart\n"
    )
    links_path = tmp_path / "generated" / "links.hpp"
    report = Emitter.generate(Tree.build(sp), tmp_path / "tasks", links_path=links_path)
    assert str(links_path) in report.created
    assert "namespace serial {" in links_path.read_text()


def test_emitter_writes_nothing_when_the_path_is_omitted(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text(
        "system:\n  blink:\n    type: polled_task\n"
        "links:\n  serial:\n    transport: uart\n"
    )
    Emitter.generate(Tree.build(sp), tmp_path / "tasks")
    assert not (tmp_path / "generated").exists()


def test_links_is_always_regenerated(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text(
        "system:\n  blink:\n    type: polled_task\n"
        "links:\n  serial:\n    transport: uart\n"
    )
    links_path = tmp_path / "generated" / "links.hpp"
    Emitter.generate(Tree.build(sp), tmp_path / "tasks", links_path=links_path)
    links_path.write_text("// hand edit\n")
    report = Emitter.generate(Tree.build(sp), tmp_path / "tasks", links_path=links_path)
    assert "// hand edit" not in links_path.read_text()
    assert str(links_path) in report.updated


def test_unchanged_links_is_not_rewritten(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text(
        "system:\n  blink:\n    type: polled_task\n"
        "links:\n  serial:\n    transport: uart\n"
    )
    links_path = tmp_path / "generated" / "links.hpp"
    Emitter.generate(Tree.build(sp), tmp_path / "tasks", links_path=links_path)
    report = Emitter.generate(Tree.build(sp), tmp_path / "tasks", links_path=links_path)
    assert str(links_path) in report.unchanged


# ------------------------------------------------------- per-link subsystems

#: Two subsystems of deliberately different widths, plus a top-level task. The
#: point of every test below is that a link pays for its own half, not both.
_SPLIT = (
    "system:\n"
    "  rotors:\n"
    "    type: scope\n"
    "    children:\n"
    "      spin:\n"
    "        type: polled_task\n"
    "        params: { level: uint8 }\n"
    "  nav:\n"
    "    type: scope\n"
    "    children:\n"
    "      fly_to:\n"
    "        type: stateful_task\n"
    "        params: { x: float, y: float, z: float }\n"
    "        returns: { eta: float, err: float }\n"
    "  failsafe:\n"
    "    type: instant_task\n"
)


def test_a_restricted_link_is_sized_for_what_it_carries(tmp_path):
    # The whole point of the feature: `esc` never carries nav.fly_to, so it must
    # not pay for its twelve bytes of parameters.
    out = _render(tmp_path, _SPLIT +
        "links:\n"
        "  esc:\n    transport: uart\n    subsystems: [rotors]\n"
        "  radio:\n    transport: wifi\n    subsystems: [nav]\n"
    )
    assert _need(out, "esc", "request") < _need(out, "radio", "request")
    assert _need(out, "esc", "reply") < _need(out, "radio", "reply")


def test_the_two_directions_are_sized_independently_per_link(tmp_path):
    # nav drives both directions here; a link carrying only rotors drives
    # neither, and its reply is the bare fixed part.
    out = _render(tmp_path, _SPLIT +
        "links:\n"
        "  esc:\n    transport: uart\n    subsystems: [rotors, failsafe]\n"
    )
    # 1 directive + 1 uid + 1 param byte; 1 uid + 1 status, nothing returned.
    assert _need(out, "esc", "request") == 3
    assert _need(out, "esc", "reply") == 2


def test_an_unrestricted_link_is_still_sized_for_the_whole_device(tmp_path):
    out = _render(tmp_path, _SPLIT +
        "links:\n"
        "  esc:\n    transport: uart\n    subsystems: [rotors]\n"
        "  radio:\n    transport: wifi\n"
    )
    # 1 + 1 + three floats.
    assert _need(out, "radio", "request") == 14


def test_two_links_carrying_the_same_subsystem_agree(tmp_path):
    out = _render(tmp_path, _SPLIT +
        "links:\n"
        "  a:\n    transport: uart\n    subsystems: [nav]\n"
        "  b:\n    transport: i2c\n    subsystems: [nav]\n"
    )
    assert _need(out, "a", "request") == _need(out, "b", "request")
    assert _need(out, "a", "reply") == _need(out, "b", "reply")


def test_a_restricted_link_emits_its_allowlist(tmp_path):
    out = _render(tmp_path, _SPLIT +
        "links:\n"
        "  esc:\n    transport: uart\n    subsystems: [rotors]\n"
    )
    body = out.split("namespace esc {")[1]
    assert "constexpr bool carries(" in body
    assert "uid ==" in body


def test_the_allowlist_names_each_task_it_admits(tmp_path):
    # A refusal in the field is a bare number; the generated header is where it
    # gets traced back to a schema path, so the comment is load-bearing.
    out = _render(tmp_path, _SPLIT +
        "links:\n"
        "  esc:\n    transport: uart\n    subsystems: [rotors]\n"
    )
    body = out.split("namespace esc {")[1]
    assert "// rotors.spin" in body


def test_an_unrestricted_link_admits_everything_unconditionally(tmp_path):
    # No uid list to walk, so the check folds away rather than costing a compare
    # per request on a link that could never refuse one.
    out = _render(tmp_path, _SPLIT +
        "links:\n  radio:\n    transport: wifi\n"
    )
    body = out.split("namespace radio {")[1]
    assert "{ return true; }" in body
    assert "uid ==" not in body


def test_a_root_level_task_reaches_the_link_that_names_it(tmp_path):
    out = _render(tmp_path, _SPLIT +
        "links:\n"
        "  esc:\n    transport: uart\n    subsystems: [rotors, failsafe]\n"
    )
    body = out.split("namespace esc {")[1]
    assert "// failsafe" in body


def test_every_link_emits_traits(tmp_path):
    # What `external_channel` is instantiated on - restricted or not, so a call
    # site spells one name either way.
    out = _render(tmp_path, _SPLIT +
        "links:\n"
        "  esc:\n    transport: uart\n    subsystems: [rotors]\n"
        "  radio:\n    transport: wifi\n"
    )
    for link in ("esc", "radio"):
        body = out.split(f"namespace {link} {{")[1]
        assert "struct traits {" in body
        for member in ("request_packet_t", "reply_packet_t", "fingerprint",
                       "request_payload_need", "reply_payload_need", "carries"):
            assert member in body, f"{link} traits is missing {member}"


def test_traits_carries_is_a_function_not_a_pointer(tmp_path):
    # A pointer would defeat the point: the call has to resolve at compile time
    # so an unrestricted link's check disappears.
    out = _render(tmp_path, _SPLIT +
        "links:\n  radio:\n    transport: wifi\n"
    )
    body = out.split("struct traits {")[1]
    assert "static constexpr bool carries(" in body
    assert "&radio::carries" not in body


def test_the_uid_type_follows_the_schema_width(tmp_path):
    # Two-byte uids must widen `carries`, or the generated header would truncate
    # every uid above 255 and admit the wrong tasks.
    wide = ("system:\n"
            "  bank:\n    type: abstract_scope\n"
            "    instances: [" + ", ".join(f"i{n}" for n in range(300)) + "]\n"
            "    children:\n      t:\n        type: polled_task\n"
            "  grp:\n    type: scope\n    children:\n      one:\n        type: polled_task\n")
    out = _render(tmp_path, wide +
        "links:\n  serial:\n    transport: uart\n    subsystems: [grp]\n"
    )
    body = out.split("namespace serial {")[1]
    assert "carries(std::uint16_t" in body


def test_the_doc_block_says_what_the_link_carries(tmp_path):
    out = _render(tmp_path, _SPLIT +
        "links:\n"
        "  esc:\n    transport: uart\n    subsystems: [rotors]\n"
        "  radio:\n    transport: wifi\n"
    )
    prose = _flat(out)
    assert "Carries `rotors`, and nothing else." in prose
    assert "Carries every subsystem" in prose
