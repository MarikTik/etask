import textwrap
from typing import List, Optional, Tuple

from etask.schema.models.link import Checksum, Link, Topology, Transport
from etask.schema.models.links import Links
from etask.schema.fingerprint import Fingerprint
from etask.schema.models.node import Node
from etask.schema.codegen.task_id_file import UID_UNDERLYING


_NAMESPACE = "generated::links"
_GUARD = "GENERATED_LINKS_HPP_"

#: Every packet size the generator emits is a multiple of this, and it is a
#: literal - never ``sizeof(std::size_t)``. ecomm asserts
#: ``PacketSize % sizeof(std::size_t) == 0``, and that word is 8 on a 64-bit
#: host but 4 on an ESP32, so rounding to the *local* word would hand the two
#: ends of the same link two different frame sizes from one schema. 8 is a
#: multiple of 4, so one number satisfies both targets; the cost is at most
#: seven wasted bytes and the benefit is a wire format that means the same
#: thing everywhere. Do not "optimize" this to the local word size.
_ALIGNMENT = 8

#: Payload bytes a request spends before the first argument: the packed
#: directive byte, then the uid. Mirrors ``protocol::request``'s wire picture.
_DIRECTIVE_BYTES = 1

#: Payload bytes a reply spends before the first result value: the uid, then
#: the status code byte. Mirrors ``protocol::reply``'s wire picture.
_STATUS_BYTES = 1

#: Why each transport got the checksum it did, for the emitted comment. Keyed
#: by whether the transport checksums for us, which is the whole of the rule.
_CHECKSUM_WHY_DEFAULTED = {
    True: (
        "the transport already checksums every byte it carries, so a second "
        "one would cost width without covering anything the first misses"
    ),
    False: (
        "a raw link corrupts frames silently, and sixteen bits is the cheapest "
        "width that catches the burst errors such links actually produce"
    ),
}


class LinksFile:
    """Renders ``links.hpp`` - one packet type pair per declared external link.

    Like ``task_id.hpp`` and ``task_list.hpp``, this is a pure projection of the
    schema and is **rewritten in full every run**: it carries no user code. What
    it deliberately does *not* carry is which serial port, socket or pins the
    transport uses - the generator cannot know that, so it stays in the user's
    ``config/wiring.hpp``, which instantiates the transport and hands it these
    types.

    ## Two packet types per link, sized independently

    ``protocol::request<Packet, Uid>`` and ``protocol::reply<Packet, Uid>`` are
    separately templated on their packet, so the two directions of one link do
    not have to be the same size. They share a *header* type - same topology,
    same sequencing, same checksum - so it is one wire format at two sizes, not
    two protocols. This matters because the traffic is asymmetric in practice: a
    control link is usually a small command producing a large telemetry reply,
    and sizing both to the larger would double the buffer for no gain.

    So each direction gets its own requirement:

    - ``request_payload_need`` = directive byte + uid + the widest task's params
    - ``reply_payload_need``   = uid + status byte + the widest return shape

    ## Why the size is computed in C++ rather than here

    A packet's total size is its payload plus ``sizeof(header_t)``, and the
    header's width depends on the link's topology (two id bytes or none), its
    sequencing (one byte or none), its checksum (the policy's field width) *and*
    on the target's padding rules. Python cannot know that number. So the
    generator emits the half it does know - the payload requirement, a literal
    computed from the schema - and lets a ``constexpr`` helper in the emitted
    header add the header size and round up. The rounding is to a literal 8 (see
    :data:`_ALIGNMENT`), which is why the helper takes no word-size parameter.
    """

    @staticmethod
    def render(root: Node) -> str:
        """Renders the whole file for a schema root.

        @param root The parsed schema root; ``root.links`` supplies the links
               and the task tree supplies the sizes they must carry.
        @return The complete text of ``generated/links.hpp``.
        """
        links: Links = root.links if root.links is not None else Links()
        uid_bytes = root.uid_bytes or 1
        every_task = LinksFile.__tasks(root)

        lines: List[str] = []
        lines.extend(LinksFile.__file_header(links))
        lines.append(f"#ifndef {_GUARD}")
        lines.append(f"#define {_GUARD}")
        lines.append("#include <cstddef>")
        if links:
            lines.append("#include <ecomm/protocol/packet.hpp>")
            lines.append("#include <ecomm/protocol/packet_header.hpp>")
            lines.append("#include <ecomm/protocol/checksum.hpp>")
            lines.append("#include <ecomm/protocol/sequence.hpp>")
            lines.append("#include <ecomm/protocol/topology.hpp>")
        lines.append("#include <cstdint>")
        lines.append("")
        lines.extend(LinksFile.__fingerprint(root))
        lines.append("")
        lines.append(f"namespace {_NAMESPACE} {{")
        lines.append("")
        lines.extend(LinksFile.__any(links))
        if links:
            lines.append("")
            lines.extend(LinksFile.__sizing_helper())
        for link in links:
            carried = LinksFile.__carried_tasks(links, link.name, every_task)
            request_need, request_driver = LinksFile.__request_need(carried, uid_bytes)
            reply_need, reply_driver = LinksFile.__reply_need(carried, uid_bytes)
            lines.append("")
            lines.extend(
                LinksFile.__link(
                    link, uid_bytes,
                    request_need, request_driver,
                    reply_need, reply_driver,
                    carried if not links.carries_everything(link.name) else None,
                )
            )
        lines.append("")
        lines.append(f"}} // namespace {_NAMESPACE}")
        lines.append(f"#endif // {_GUARD}")
        return "\n".join(lines) + "\n"

    # ------------------------------------------------------------------ sizing

    @staticmethod
    def __request_need(carried: List[Node], uid_bytes: int) -> Tuple[int, Optional[str]]:
        """The request payload one link's tasks must fit in.

        A request is ``[directive][uid][args...]``, so the requirement is those
        two fixed fields plus the widest parameter list. Widest among the tasks
        *this link carries*, which is what makes the sizing per-link: a link
        that never carries the fat task does not pay for it, and on a device
        whose subsystems differ in width that is most of the frame.

        @param carried The tasks this link carries.
        @param uid_bytes The uid width shared by every task.
        @return The byte count, and the name of the task that drove it (``None``
                when no carried task takes parameters, so nothing drove it).
        """
        widest, driver = 0, None
        for task in carried:
            size = sum(param.wire_size or 0 for param in task.params or [])
            if size > widest:
                widest, driver = size, LinksFile.__path(task)
        return _DIRECTIVE_BYTES + uid_bytes + widest, driver

    @staticmethod
    def __reply_need(carried: List[Node], uid_bytes: int) -> Tuple[int, Optional[str]]:
        """The reply payload one link's results must fit in.

        A reply is ``[uid][status][result...]``, so the requirement is those two
        fixed fields plus the widest *shape* a carried task can reply with.
        Shapes, not tasks: a task that returns different values on different
        status codes is sized by its widest branch, since only one is ever on
        the wire at a time but any of them may be.

        Sized independently of the request direction, and often driven by a
        different subsystem entirely - a sensor suite takes no arguments and
        replies with a lot, a motor bus the reverse.

        @param carried The tasks this link carries.
        @param uid_bytes The uid width shared by every task.
        @return The byte count, and the name of the task and status that drove
                it (``None`` when nothing carried returns anything).
        """
        widest, driver = 0, None
        for task in carried:
            for shape in task.returns or []:
                if shape.wire_size > widest:
                    widest = shape.wire_size
                    driver = f"{LinksFile.__path(task)} on {shape.name}"
        return uid_bytes + _STATUS_BYTES + widest, driver

    @staticmethod
    def __carried_tasks(links: Links, name: str, every_task: List[Node]) -> List[Node]:
        """The tasks one link carries, in declaration order.

        @param links The parsed links, holding the resolved subsystem sets.
        @param name The link's name.
        @param every_task Every task in the system.
        @return The carried subset - all of them for an unrestricted link.
        """
        if links.carries_everything(name):
            return every_task
        carried = links.uids_for(name, frozenset())
        return [task for task in every_task if task.uid in carried]

    @staticmethod
    def __tasks(node: Node) -> List[Node]:
        """Every task in the tree, root first, in declaration order."""
        tasks = [node] if node.is_task else []
        for child in node.children.values():
            tasks.extend(LinksFile.__tasks(child))
        return tasks

    @staticmethod
    def __path(task: Node) -> str:
        """A task's dotted schema path, for naming it in a comment."""
        parts: List[str] = []
        walk: Optional[Node] = task
        while walk is not None and walk.parent is not None:
            parts.append(walk.name)
            walk = walk.parent
        return ".".join(reversed(parts)) or task.name

    # ------------------------------------------------------------------- parts

    @staticmethod
    def __file_header(links: Links) -> List[str]:
        lines = [
            "/**",
            "* @file links.hpp",
            "*",
            "* @brief The packet types for this system's external links.",
            "*",
        ]
        count = len(links)
        if count:
            lines.extend(LinksFile.__wrap(
                f"{count} external link{'' if count == 1 else 's'}: "
                f"{', '.join(links.names)}. Each becomes a namespace holding two "
                "packet types - one per direction - plus the constants its channel "
                "needs.",
                indent="",
            ))
            lines.append("*")
            lines.extend(LinksFile.__wrap(
                "The two directions are sized independently: `protocol::request` and "
                "`protocol::reply` are separately templated, and the traffic is rarely "
                "symmetric (a one-byte command can produce a forty-byte telemetry "
                "reply). They share a header type, so it stays one wire format at two "
                "sizes rather than becoming two protocols.",
                indent="",
            ))
            lines.append("*")
            lines.extend(LinksFile.__wrap(
                "What is NOT here: which port, socket or pins the transport uses. The "
                "schema cannot know that. Instantiate the transport in "
                "config/wiring.hpp and hand it these types.",
                indent="",
            ))
        else:
            lines.extend(LinksFile.__wrap(
                "This system declares no `links:`, so it speaks over the internal "
                "channel only - which is what the great majority of projects do. The "
                "file is generated anyway, and empty of packet types by design: a "
                "config header can include it and branch on `any` without having to "
                "know whether the schema declared a link.",
                indent="",
            ))
        lines.extend([
            "*",
            "* @warning GENERATED - DO NOT EDIT. Regenerated in full from the schema",
            "*          on every generate; hand edits are overwritten. Regenerate via the",
            "*          CMake `etask-generate` target, or `etask generate`.",
            "*/",
        ])
        return lines

    @staticmethod
    def __wrap(text: str, indent: str = "    ", width: int = 88) -> List[str]:
        """Wraps prose into ``* ``-prefixed comment lines at ``indent``."""
        return [
            f"{indent}* {line}"
            for line in textwrap.wrap(text, width - len(indent) - 2)
        ]

    @staticmethod
    def __fingerprint(root: Node) -> List[str]:
        """Renders the schema fingerprint, in the parent `generated` namespace.

        It describes the whole wire contract - every uid, argument list, result
        shape and link policy - so it belongs beside the task lists rather than
        inside `links`, even though the handshake that carries it is a per-link
        affair.

        @param root The parsed schema root.
        @return The lines declaring `generated::schema_fingerprint`.
        """
        value = Fingerprint.hex(root)
        return [
            "namespace generated {",
            "",
            "    /**",
            "    * @brief This schema's wire contract, reduced to eight bytes.",
            "    *",
            "    * Two peers built from the same schema agree on every uid, every argument",
            "    * list, every result shape and every link's frame layout. Two peers built",
            "    * from different ones may agree on all of the layout and none of the",
            "    * meaning: the frames parse, the checksum passes, and this device runs the",
            "    * wrong task with plausible-looking arguments. That is what this catches.",
            "    *",
            "    * Exchanged in a fixed handshake preamble at connect - fixed because two",
            "    * peers that disagree about a header cannot use a normal frame to say so.",
            "    * A link whose peer sends a different value refuses task traffic rather",
            "    * than misreading it; the other links keep working.",
            "    *",
            "    * Derived from a canonical rendering of the schema, so reordering the YAML",
            "    * cannot change it and any real contract change must.",
            "    */",
            f"    inline constexpr std::uint64_t schema_fingerprint = 0x{value.upper()}ULL;",
            "",
            "} // namespace generated",
        ]

    @staticmethod
    def __any(links: Links) -> List[str]:
        """Whether the system has any external link at all.

        Emitted either way, so a config header can include this file
        unconditionally and branch on the constant rather than on whether the
        schema happened to declare a ``links:`` section.
        """
        lines = ["    /**", "    * @brief Whether this system declares any external link."]
        lines.append("    *")
        if links:
            lines.extend(LinksFile.__wrap(
                "It does, so each one's namespace follows. Emitted either way so a "
                "config header can include this file unconditionally and branch on "
                "the constant instead of on the shape of the schema."
            ))
        else:
            lines.extend(LinksFile.__wrap(
                "It does not, so nothing else is generated here - the system speaks "
                "over the internal channel only. Emitted either way so a config "
                "header can include this file unconditionally and branch on the "
                "constant instead of on the shape of the schema."
            ))
        lines.append("    */")
        lines.append(f"    inline constexpr bool any = {'true' if links else 'false'};")
        return lines

    @staticmethod
    def __sizing_helper() -> List[str]:
        """The constexpr that turns a payload requirement into a packet size.

        This is the piece Python cannot do: ``sizeof(header_t)`` depends on the
        link's policies *and* on the target, so the generator emits the payload
        requirement it knows and lets the compiler add the rest.
        """
        lines = ["    /**", "    * @brief The packet size that carries `PayloadNeed` payload bytes."]
        lines.append("    *")
        lines.extend(LinksFile.__wrap(
            "A packet's payload is `PacketSize - sizeof(header_t)`, and the header's "
            "width depends on the link's topology, sequencing and checksum - and on "
            "the target's layout rules. The generator cannot compute that, so it "
            "emits the payload requirement (which it does know, from the schema) and "
            "this adds the header and rounds up."
        ))
        lines.append("    *")
        lines.extend(LinksFile.__wrap(
            "The rounding is to a literal 8, NOT to `sizeof(std::size_t)`. ecomm "
            "asserts `PacketSize % sizeof(std::size_t) == 0`, and that word is 8 on a "
            "64-bit host but 4 on an ESP32 - so rounding to the local word would give "
            "the PC client and the device two different frame sizes from one schema, "
            "and both would compile clean before disagreeing on the wire. 8 is a "
            "multiple of 4, so one number satisfies every target. The cost is under "
            "eight bytes per frame."
        ))
        lines.append("    *")
        lines.extend(LinksFile.__wrap(
            "The `+ 1` is division-then-increment, so the result is the next multiple "
            "of 8 *strictly above* header + payload, never equal to it. That is "
            "deliberate: ecomm's other assert is `PacketSize > sizeof(header_t)`, and "
            "a total that landed exactly on a multiple of 8 would otherwise round to "
            "itself. It costs a full 8 bytes in that one case and buys an invariant "
            "that holds for every schema."
        ))
        lines.append("    *")
        lines.append("    * @tparam PayloadNeed Payload bytes the direction must carry.")
        lines.append("    * @tparam Header The link's header type, whose size is added.")
        lines.append("    * @return The total packet size, a multiple of 8.")
        lines.append("    */")
        lines.append("    template<std::size_t PayloadNeed, typename Header>")
        lines.append("    inline constexpr std::size_t packet_size_for =")
        lines.append(f"        ((PayloadNeed + sizeof(Header)) / {_ALIGNMENT} + 1) * {_ALIGNMENT};")
        return lines

    @staticmethod
    def __link(
        link: Link,
        uid_bytes: int,
        request_need: int,
        request_driver: Optional[str],
        reply_need: int,
        reply_driver: Optional[str],
        carried: Optional[List[Node]],
    ) -> List[str]:
        """One link's namespace: its header type, both packets, its constants.

        @param carried The tasks this link carries, or ``None`` when it carries
               everything - which emits an unconditional `carries()` rather than
               a list, so an unrestricted link costs nothing at runtime.
        """
        lines: List[str] = []
        lines.extend(LinksFile.__link_doc(link, carried))
        lines.append(f"    namespace {link.name} {{")
        lines.append("")
        lines.extend(LinksFile.__header_alias(link))
        lines.append("")
        lines.extend(LinksFile.__need(
            "request", request_need, request_driver,
            f"the packed directive byte, the {uid_bytes}-byte uid, and the "
            "widest task's arguments",
            _DIRECTIVE_BYTES + uid_bytes,
        ))
        lines.append("")
        lines.extend(LinksFile.__need(
            "reply", reply_need, reply_driver,
            f"the {uid_bytes}-byte uid, the status byte, and the widest result "
            "any task can reply with",
            uid_bytes + _STATUS_BYTES,
        ))
        lines.append("")
        lines.extend(LinksFile.__packet("request", request_need, reply_need))
        lines.append("")
        lines.extend(LinksFile.__packet("reply", reply_need, request_need))
        lines.append("")
        lines.extend(LinksFile.__carries(link, carried, uid_bytes))
        lines.append("")
        lines.extend(LinksFile.__reliability(link))
        lines.append("")
        lines.extend(LinksFile.__traits(link, uid_bytes))
        lines.append(f"    }} // namespace {link.name}")
        return lines

    @staticmethod
    def __traits(link: Link, uid_bytes: int) -> List[str]:
        """The one type `external_channel` is instantiated on.

        Everything above is a separate name so it can be read, documented and
        reasoned about on its own. The channel takes them as a bundle instead,
        because they are not independent choices: a link's two packets, its
        fingerprint and its uid set all come from the same schema, and letting a
        call site pass them one at a time is letting it pair a link's packets
        with another link's allowlist. Passing the whole link makes that
        unspellable.
        """
        lines = ["        /**", "        * @brief This link, as one type."]
        lines.append("        *")
        lines.extend(LinksFile.__wrap(
            "What `external_channel` is instantiated on. Bundles the two packet "
            "types, the payload each direction must carry, the schema fingerprint "
            "the handshake exchanges, and which uids this link accepts - so a "
            "channel is built from one name and cannot be handed a mismatched set.",
            indent="        ",
        ))
        lines.append("        */")
        name = link.name
        lines.append("        struct traits {")
        lines.append("            /// @brief The packet a request travels in.")
        lines.append(f"            using request_packet_t = {name}::request_packet_t;")
        lines.append("")
        lines.append("            /// @brief The packet a reply travels in.")
        lines.append(f"            using reply_packet_t = {name}::reply_packet_t;")
        lines.append("")
        lines.append("            /// @brief The wire contract both peers must agree on.")
        lines.append(
            "            static constexpr std::uint64_t fingerprint = "
            "generated::schema_fingerprint;"
        )
        lines.append("")
        lines.append("            /// @brief Payload bytes a request must carry. "
                     "@see request_payload_need")
        lines.append(
            "            static constexpr std::size_t request_payload_need = "
            f"{name}::request_payload_need;"
        )
        lines.append("")
        lines.append("            /// @brief Payload bytes a reply must carry. "
                     "@see reply_payload_need")
        lines.append(
            "            static constexpr std::size_t reply_payload_need = "
            f"{name}::reply_payload_need;"
        )
        lines.append("")
        lines.append("            /**")
        lines.append("            * @brief Whether this link carries a uid.")
        lines.append("            *")
        lines.extend(LinksFile.__wrap(
            "A static member function rather than a pointer to one, so the call is "
            "resolved at compile time: on a link that carries everything the body is "
            "`return true`, and the check disappears entirely.",
            indent="            ",
        ))
        lines.append("            *")
        lines.append("            * @param uid The uid a request named.")
        lines.append("            * @return Whether this link carries that task.")
        lines.append("            */")
        lines.append(
            f"            static constexpr bool carries({LinksFile.__uid_type(uid_bytes)} uid) noexcept"
        )
        lines.append(f"            {{ return {name}::carries(uid); }}")
        lines.append("        };")
        return lines

    @staticmethod
    def __link_doc(link: Link, carried: Optional[List[Node]]) -> List[str]:
        """The namespace's doc block: what this link is, and why it looks so."""
        lines = ["    /**", f"    * @brief The `{link.name}` link, over {link.transport.value}."]
        lines.append("    *")
        lines.extend(LinksFile.__wrap(LinksFile.__subsystems_why(link, carried)))
        lines.append("    *")
        lines.extend(LinksFile.__wrap(LinksFile.__topology_why(link)))
        lines.append("    *")
        lines.extend(LinksFile.__wrap(LinksFile.__checksum_why(link)))
        lines.append("    *")
        lines.extend(LinksFile.__wrap(LinksFile.__reliable_why(link)))
        lines.append("    */")
        return lines

    @staticmethod
    def __subsystems_why(link: Link, carried: Optional[List[Node]]) -> str:
        """Why this link's frames are the size they are, in subsystem terms."""
        if carried is None:
            return (
                "Carries every subsystem, because the schema declared no "
                "`subsystems:` for this link. Its frames are therefore sized for "
                "the widest task on the whole device. Naming the subsystems this "
                "link actually reaches would shrink them."
            )
        declared = ", ".join(f"`{name}`" for name in link.subsystems or ())
        return (
            f"Carries {declared}, and nothing else. Frames are sized for the "
            f"widest of those {len(carried)} task(s) rather than for the whole "
            "device, and a request for any other uid is refused with "
            "`task_undefined_on_this_link` - the task exists, this wire does not "
            "carry it."
        )

    @staticmethod
    def __carries(link: Link, carried: Optional[List[Node]], uid_bytes: int) -> List[str]:
        """The link's uid allowlist, as a constexpr predicate.

        Emitted for every link, restricted or not, so `external_channel` can call
        it unconditionally. The unrestricted form ignores its argument and
        returns true, which the optimizer removes entirely - a link that carries
        everything pays nothing for the check.
        """
        lines = ["        /**", "        * @brief Whether this link carries a task."]
        lines.append("        *")
        if carried is None:
            lines.extend(LinksFile.__wrap(
                "Always true: this link carries every subsystem, so there is no uid "
                "to refuse. The parameter is unnamed to say so, and the call folds "
                "away at the call site.",
                indent="        ",
            ))
            lines.append("        *")
            lines.append("        * @return `true`, for any uid.")
            lines.append("        */")
            lines.append(
                f"        constexpr bool carries({LinksFile.__uid_type(uid_bytes)}) noexcept "
                "{ return true; }"
            )
            return lines

        lines.extend(LinksFile.__wrap(
            "This link declares `subsystems:`, so it carries only the uids beneath "
            "them. A request for any other uid is refused before it is dispatched: "
            "the task exists on this device, but not on this wire.",
            indent="        ",
        ))
        lines.append("        *")
        lines.append("        * @param uid The uid a request named.")
        lines.append("        * @return Whether this link carries that task.")
        lines.append("        */")
        lines.append(
            f"        constexpr bool carries({LinksFile.__uid_type(uid_bytes)} uid) noexcept"
        )
        lines.append("        {")
        lines.append("            return")
        # One uid per line with its path, so a refusal can be traced back to the
        # schema by reading the generated header rather than by decoding a number.
        for index, task in enumerate(sorted(carried, key=lambda t: t.uid or 0)):
            terminator = ";" if index == len(carried) - 1 else " or"
            lines.append(
                f"                uid == {LinksFile.__uid_literal(task.uid, uid_bytes)}"
                f"{terminator}   // {LinksFile.__path(task)}"
            )
        lines.append("        }")
        return lines

    @staticmethod
    def __uid_literal(uid: Optional[int], uid_bytes: int) -> str:
        """A uid as a hex literal of the schema's width."""
        return f"0x{uid or 0:0{uid_bytes * 2}X}"

    @staticmethod
    def __uid_type(uid_bytes: int) -> str:
        """The C++ type a uid of this width is.

        Spelled concretely rather than as a manager's ``task_uid_t``: this file
        describes the wire, and must not depend on which managers a project
        composes. The two agree because both follow the schema's uid width.

        @param uid_bytes The schema's uid width.
        @return The fixed-width integer type name.
        """
        return UID_UNDERLYING[uid_bytes]

    @staticmethod
    def __topology_why(link: Link) -> str:
        if link.topology is Topology.NETWORK:
            return (
                "Topology `network`: frames carry a sender and a receiver id, two "
                "header bytes, because this link reaches more than one peer and a "
                "frame that did not name its destination could not be routed."
            )
        return (
            "Topology `point_to_point`: this link has exactly one peer, so an "
            "address field would be the same constant in every frame. Those two "
            "header bytes are not spent."
        )

    @staticmethod
    def __checksum_why(link: Link) -> str:
        defaulted = link.checksum is Link.default_checksum(link.transport)
        if link.checksum is Checksum.NONE:
            reason = (
                _CHECKSUM_WHY_DEFAULTED[True]
                if link.transport.guarantees_integrity
                else "the schema asked for none"
            )
            return (
                f"Checksum `none`: no FCS field in the header, because {reason}."
            )
        why = (
            _CHECKSUM_WHY_DEFAULTED[False]
            if defaulted
            else f"the schema declared `checksum: {link.checksum.value}`"
        )
        return (
            f"Checksum `{link.checksum.value}`: the header carries an FCS field of "
            f"that policy's width, because {why}."
        )

    @staticmethod
    def __reliable_why(link: Link) -> str:
        if link.reliable:
            return (
                "Reliable: the framework sequences frames and resends the "
                "unacknowledged ones, so the header carries a one-byte sequence "
                "number. Sequencing is not a separate choice - `reliable_channel` "
                "cannot match an acknowledgement to a frame without it, and "
                "static_asserts on it - so it follows from reliability rather than "
                "being asked for."
            )
        if link.transport.guarantees_delivery:
            return (
                f"Not reliable: `{link.transport.value}` already delivers every frame "
                "in order, so layering the framework's own guarantee on top would add "
                "a sequence byte, a retry timer and a resend buffer to re-guarantee "
                "what the transport has already guaranteed. No sequence field."
            )
        return (
            "Not reliable: the schema declared `reliable: false`, so a lost frame "
            "stays lost and the header carries no sequence number. Nothing here "
            "detects the loss - the application must."
        )

    @staticmethod
    def __header_alias(link: Link) -> List[str]:
        """The link's three policies, and the header type they compose.

        The policies get names of their own because both packet types need all
        three - ``packet`` is templated on them directly, not on a header - and
        spelling them three times is three chances for the request and the reply
        to drift apart into two wire formats that still compile.
        """
        lines = ["        /// @brief Whether frames name a destination."]
        lines.append(
            f"        inline constexpr ecomm::protocol::topology link_topology ="
        )
        lines.append(f"            ecomm::protocol::topology::{link.topology.value};")
        lines.append("")
        lines.append("        /// @brief Whether frames carry a sequence number.")
        lines.append(f"        using sequence_policy = {LinksFile.__sequence(link)};")
        lines.append("")
        lines.append("        /// @brief The integrity policy frames carry.")
        lines.append(
            f"        using checksum_policy = ecomm::protocol::{link.checksum.value};"
        )
        lines.append("")
        lines.append("        /**")
        lines.append("        * @brief The header both directions carry.")
        lines.append("        *")
        lines.extend(LinksFile.__wrap(
            "One header type for the whole link, because `external_channel` "
            "static_asserts that a link's request and reply packets share one: the "
            "two packets differ in size, but they are the same wire format, and a "
            "link whose two directions disagreed about topology or checksum would "
            "not be one link.",
            indent="        ",
        ))
        lines.append("        */")
        lines.append("        using header_t = ecomm::protocol::packet_header<")
        lines.append("            link_topology, sequence_policy, checksum_policy>;")
        return lines

    @staticmethod
    def __sequence(link: Link) -> str:
        return (
            "ecomm::protocol::sequenced"
            if link.sequenced
            else "ecomm::protocol::no_sequence"
        )

    @staticmethod
    def __need(
        direction: str, need: int, driver: Optional[str], breakdown: str, fixed: int
    ) -> List[str]:
        """One direction's payload requirement, with where the number came from."""
        variable = need - fixed
        if driver is None:
            source = (
                f"No task {'takes parameters' if direction == 'request' else 'returns anything'}, "
                f"so the variable part is 0 and this is the fixed part alone."
            )
        else:
            source = (
                f"The widest is `{driver}` at {variable} byte"
                f"{'' if variable == 1 else 's'}, which is where a surprising number "
                "comes from - change that task and this changes."
            )
        lines = [
            "        /**",
            f"        * @brief Payload bytes a {direction} must be able to carry.",
            "        *",
        ]
        lines.extend(LinksFile.__wrap(
            f"{fixed} fixed + {variable} variable: {breakdown}.", indent="        "
        ))
        lines.append("        *")
        lines.extend(LinksFile.__wrap(source, indent="        "))
        lines.append("        */")
        lines.append(
            f"        inline constexpr std::size_t {direction}_payload_need = {need};"
        )
        return lines

    @staticmethod
    def __packet(direction: str, need: int, other_need: int) -> List[str]:
        """One direction's packet type."""
        other = "reply" if direction == "request" else "request"
        if need == other_need:
            note = (
                f"The same requirement as the {other} here, so the two packets will "
                "come out the same size - but they are still separate types, and one "
                "task gaining a wider argument list or result will part them."
            )
        else:
            bigger = "larger" if need > other_need else "smaller"
            note = (
                f"{need} bytes against the {other}'s {other_need}: this direction is "
                f"the {bigger} one, and sizing both to the wider would spend the "
                "difference in every buffer for nothing."
            )
        lines = [
            "        /**",
            f"        * @brief The packet a {direction} travels in.",
            "        *",
        ]
        lines.extend(LinksFile.__wrap(note, indent="        "))
        lines.append("        *")
        lines.extend(LinksFile.__wrap(
            "Its size is the payload requirement plus this link's header, rounded up "
            "to a multiple of 8 - computed by the compiler, since only it knows how "
            "wide the header is on this target. See `packet_size_for`.",
            indent="        ",
        ))
        lines.append("        */")
        lines.append(f"        using {direction}_packet_t = ecomm::protocol::packet<")
        lines.append(
            f"            packet_size_for<{direction}_payload_need, header_t>,"
        )
        lines.append("            link_topology, sequence_policy, checksum_policy>;")
        return lines

    @staticmethod
    def __reliability(link: Link) -> List[str]:
        """The constants ``wiring.hpp`` feeds to the channel it builds."""
        lines = [
            "        /**",
            "        * @brief Whether to wrap this link's channel in `reliable_channel`.",
            "        *",
        ]
        lines.extend(LinksFile.__wrap(
            "Read by config/wiring.hpp, which is where the channel is actually built: "
            "the schema decides the policy, the user's file supplies the transport it "
            "applies to.",
            indent="        ",
        ))
        lines.append("        */")
        lines.append(
            f"        inline constexpr bool reliable = {'true' if link.reliable else 'false'};"
        )
        if not link.reliable:
            lines.append("")
            lines.extend(LinksFile.__note(
                "No `retries` or `buffer_depth` here: nothing is ever resent on an "
                "unreliable link, so a retry budget would be a number no code reads."
            ))
            return lines
        lines.append("")
        lines.append("        /// @brief Resends before a frame is given up on.")
        lines.append(
            f"        inline constexpr unsigned retries = {link.retries};"
        )
        lines.append("")
        lines.append(
            "        /// @brief How many unacknowledged frames may be in flight; sizes"
        )
        lines.append("        ///        the resend buffer, so it is this link's real memory cost.")
        lines.append(
            f"        inline constexpr unsigned buffer_depth = {link.buffer_depth};"
        )
        return lines

    @staticmethod
    def __note(text: str, indent: str = "        ") -> List[str]:
        """Free-standing prose that documents an *absence*, so it attaches to no
        declaration and must not be a doc comment."""
        return [
            f"{indent}// {line}"
            for line in textwrap.wrap(text, 88 - len(indent) - 3)
        ]
