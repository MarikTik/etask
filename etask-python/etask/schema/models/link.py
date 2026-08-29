from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from etask.schema.errors.schema_shape_error import SchemaShapeError


class Transport(Enum):
    """What physically carries a link's bytes.

    The transport is the one thing a link cannot infer: everything else in
    :class:`Link` has a defensible default *given* the transport, because the
    transport decides what the medium already guarantees. A raw byte pipe
    (uart/i2c) guarantees nothing, a datagram medium (wifi) guarantees no
    ordering, and tcp guarantees both integrity and ordering - which is why it
    is the one transport that refuses the framework's own guarantees rather
    than stacking a second copy on top of them.
    """

    UART = "uart"
    WIFI = "wifi"
    I2C = "i2c"
    TCP = "tcp"
    #: An application-supplied transport object. The generator knows nothing
    #: about what it guarantees, so it defaults like a raw link: checksummed
    #: and reliable. A user who knows better states otherwise explicitly.
    CUSTOM = "custom"

    @property
    def guarantees_delivery(self) -> bool:
        """Whether the transport already delivers every byte, in order.

        True only for tcp. Layering ``reliable_channel`` over a transport that
        already does this buys nothing and costs a sequence field, a retry
        timer and a resend buffer, so the schema rejects it rather than letting
        a project pay twice.
        """
        return self is Transport.TCP

    @property
    def guarantees_integrity(self) -> bool:
        """Whether the transport already checksums what it carries.

        True only for tcp, which carries its own crc32. Wifi checksums at the
        link layer, but a wifi link here is a UDP-shaped datagram path whose
        payload can still be truncated or mis-delivered by everything between
        the two radios, so it is not counted.
        """
        return self is Transport.TCP

    @staticmethod
    def parse(raw: object, path: str) -> "Transport":
        """Resolves the ``transport:`` value.

        @param raw The declared value.
        @param path Schema path, for the error message.
        @return The transport.
        @throws SchemaShapeError If it names no known transport.
        """
        for transport in Transport:
            if transport.value == raw:
                return transport
        raise SchemaShapeError(
            path,
            f"unknown transport {raw!r}; expected one of {Transport.names()}. "
            "Use 'custom' for a transport this framework does not model and "
            "supply the object yourself in config/wiring.hpp.",
        )

    @staticmethod
    def names() -> str:
        """The declarable transport names, for error messages."""
        return ", ".join(transport.value for transport in Transport)


class Topology(Enum):
    """Whether a link's frames need to say who they are for.

    ``point_to_point`` has exactly one peer, so an address field would be a
    constant on the wire. ``network`` carries one, because it does not.
    """

    POINT_TO_POINT = "point_to_point"
    NETWORK = "network"

    @staticmethod
    def parse(raw: object, path: str) -> "Topology":
        """Resolves the ``topology:`` value.

        @param raw The declared value.
        @param path Schema path, for the error message.
        @return The topology.
        @throws SchemaShapeError If it names no known topology.
        """
        for topology in Topology:
            if topology.value == raw:
                return topology
        raise SchemaShapeError(
            path,
            f"unknown topology {raw!r}; expected one of {Topology.names()}. "
            "Use 'point_to_point' when the link has exactly one peer and "
            "'network' when frames must name their destination.",
        )

    @staticmethod
    def names() -> str:
        """The declarable topology names, for error messages."""
        return ", ".join(topology.value for topology in Topology)


class Checksum(Enum):
    """The integrity policy a link's frames carry.

    Every member names a policy struct that exists in
    ``ecomm/protocol/checksum.hpp``; the value is the C++ struct name verbatim,
    so the emitter can spell ``ecomm::protocol::<value>`` without a second
    table to keep in step.

    The ``*_reflected`` variants are the LSB-first CRCs the ESP mask ROM
    implements. They are *different checksums*, not faster spellings of the
    plain ones - both peers must name the same policy - so they are offered but
    never defaulted to.
    """

    NONE = "none"
    SUM8 = "sum8"
    SUM16 = "sum16"
    SUM32 = "sum32"
    CRC8 = "crc8"
    CRC16 = "crc16"
    CRC32 = "crc32"
    CRC64 = "crc64"
    CRC8_REFLECTED = "crc8_reflected"
    CRC16_REFLECTED = "crc16_reflected"
    CRC32_REFLECTED = "crc32_reflected"
    FLETCHER16 = "fletcher16"
    FLETCHER32 = "fletcher32"
    ADLER32 = "adler32"
    INTERNET16 = "internet16"

    @property
    def is_none(self) -> bool:
        """Whether this link carries no checksum field at all."""
        return self is Checksum.NONE

    @staticmethod
    def parse(raw: object, path: str) -> "Checksum":
        """Resolves the ``checksum:`` value.

        @param raw The declared value.
        @param path Schema path, for the error message.
        @return The checksum policy.
        @throws SchemaShapeError If it names no policy ecomm implements.
        """
        for checksum in Checksum:
            if checksum.value == raw:
                return checksum
        raise SchemaShapeError(
            path,
            f"unknown checksum {raw!r}; expected one of {Checksum.names()}. "
            "These are the policy structs ecomm/protocol/checksum.hpp defines; "
            "a name outside the list has no type to instantiate.",
        )

    @staticmethod
    def names() -> str:
        """The declarable checksum names, for error messages."""
        return ", ".join(checksum.value for checksum in Checksum)


#: Per-transport defaults. Each is a *justified* choice, not a house style: see
#: :meth:`Link.default_topology`, :meth:`Link.default_checksum` and
#: :meth:`Link.default_reliable` for the reasoning, which the emitter is
#: expected to repeat in a comment so a reader never has to guess why their
#: UART link ended up with crc16.
_DEFAULT_RETRIES = 3
_DEFAULT_BUFFER_DEPTH = 4

#: Keys a link body may declare. Anything else is a typo worth naming, since a
#: silently ignored key would leave the schema claiming a behavior the firmware
#: does not have.
_FIELDS = ("transport", "topology", "checksum", "reliable", "retries", "buffer_depth")

#: The two keys that only mean something on a reliable link.
_RELIABLE_ONLY = ("retries", "buffer_depth")


@dataclass(frozen=True)
class Link:
    """One external communication link, as declared under ``links:``.

    A link is everything the generated packet type needs that the schema can
    know: how frames are addressed, how their integrity is checked, and whether
    the framework layers its own delivery guarantee on top of the transport.
    What it deliberately does *not* hold is which serial port, socket or pins
    the transport uses - the generator cannot know that, so the user keeps it
    in ``config/wiring.hpp``.

    Every field but :attr:`name` and :attr:`transport` has a per-transport
    default, so the shortest honest link declaration is one line of transport.
    """

    #: The link's name, and the C++ namespace it becomes.
    name: str

    #: What carries the bytes. The only field with no default.
    transport: Transport

    #: Whether frames name a destination.
    topology: Topology

    #: The integrity policy frames carry.
    checksum: Checksum

    #: Whether the framework guarantees delivery itself, by sequencing frames
    #: and resending unacknowledged ones.
    reliable: bool

    #: Resends before a frame is given up on. ``None`` on a non-reliable link,
    #: where there is nothing to resend.
    retries: Optional[int] = None

    #: How many unacknowledged frames may be in flight. ``None`` on a
    #: non-reliable link.
    buffer_depth: Optional[int] = None

    @property
    def sequenced(self) -> bool:
        """Whether frames carry a sequence number.

        Not a schema field: it is a consequence. ``reliable_channel`` cannot
        match an acknowledgement to a frame without one and static_asserts on
        it, so the generator emits ``sequenced`` for every reliable link rather
        than making the user restate a thing they have no freedom about. A
        non-reliable link pays nothing for a field nobody reads.
        """
        return self.reliable

    @staticmethod
    def default_topology(transport: Transport) -> Topology:
        """The topology a transport implies when the schema is silent.

        uart and i2c reach one peer as configured here (i2c addresses a device,
        but this link is that device), so an address field would be a constant.
        wifi and tcp are routed media where it is not.
        """
        return (
            Topology.NETWORK
            if transport in (Transport.WIFI, Transport.TCP)
            else Topology.POINT_TO_POINT
        )

    @staticmethod
    def default_checksum(transport: Transport) -> Checksum:
        """The checksum a transport implies when the schema is silent.

        ``none`` for tcp, which already carries its own crc32; ``crc16`` for
        everything else, because a raw link corrupts frames silently and
        sixteen bits is the cheapest width that catches the burst errors those
        links actually produce.
        """
        return Checksum.NONE if transport.guarantees_integrity else Checksum.CRC16

    @staticmethod
    def default_reliable(transport: Transport) -> bool:
        """Whether a transport gets the framework's delivery guarantee by default.

        True everywhere but tcp: silent loss on a raw link is a worse failure
        than the latency and the sequence field that avoiding it costs. tcp
        already guarantees ordered delivery, so it is forced false.
        """
        return not transport.guarantees_delivery

    @staticmethod
    def parse(name: str, body: object, path: str) -> "Link":
        """Builds one link from its schema body.

        @param name The link's name, already validated as an identifier by the
               caller (which owns the identifier rules for the whole schema).
        @param body The raw mapping under that name.
        @param path Schema path, for error messages.
        @return The parsed link, with every unstated field defaulted.
        @throws SchemaShapeError If the body is malformed, names an unknown
                key or value, or asks for a combination that contradicts what
                the transport already provides.
        """
        if not isinstance(body, dict):
            raise SchemaShapeError(
                path,
                "a link body must be a mapping; at minimum it names a transport:\n"
                f"        {name}:\n"
                "          transport: uart",
            )

        Link.__reject_unknown_keys(body, path)

        if "transport" not in body:
            raise SchemaShapeError(
                path,
                "missing required 'transport'. Everything else about a link has a "
                f"default once the transport is known, so name one of {Transport.names()}.",
            )
        transport = Transport.parse(body["transport"], path)

        topology = (
            Topology.parse(body["topology"], path)
            if "topology" in body
            else Link.default_topology(transport)
        )
        checksum = Link.__resolve_checksum(body, transport, path)
        reliable = Link.__resolve_reliable(body, transport, path)
        retries, buffer_depth = Link.__resolve_retry_policy(body, reliable, path)

        return Link(
            name=name,
            transport=transport,
            topology=topology,
            checksum=checksum,
            reliable=reliable,
            retries=retries,
            buffer_depth=buffer_depth,
        )

    # ------------------------------------------------------------- field rules

    @staticmethod
    def __reject_unknown_keys(body: dict, path: str) -> None:
        """Rejects a key the link grammar has no meaning for.

        @param body The raw link mapping.
        @param path Schema path, for the error message.
        @throws SchemaShapeError If any key is not in the grammar.
        """
        unknown = [key for key in body if key not in _FIELDS]
        if not unknown:
            return
        raise SchemaShapeError(
            path,
            f"unknown link {'key' if len(unknown) == 1 else 'keys'} "
            f"{', '.join(repr(u) for u in sorted(unknown))}; "
            f"expected one of {', '.join(_FIELDS)}. "
            "Which port, socket or pins the transport uses is not a schema "
            "question - it belongs in config/wiring.hpp.",
        )

    @staticmethod
    def __resolve_checksum(body: dict, transport: Transport, path: str) -> Checksum:
        """Resolves ``checksum:``, refusing to checksum twice.

        @param body The raw link mapping.
        @param transport The link's transport.
        @param path Schema path, for the error message.
        @return The checksum policy.
        @throws SchemaShapeError If a transport that already checksums is asked
                to carry a second one.
        """
        if "checksum" not in body:
            return Link.default_checksum(transport)

        checksum = Checksum.parse(body["checksum"], path)
        if transport.guarantees_integrity and not checksum.is_none:
            raise SchemaShapeError(
                path,
                f"transport '{transport.value}' already checksums every byte it "
                f"carries, so '{checksum.value}' would be a second checksum over "
                "data the first one already covers - cost with no coverage gained. "
                "Drop the 'checksum' key (it defaults to none here), or move to a "
                "transport that does not checksum for you.",
            )
        return checksum

    @staticmethod
    def __resolve_reliable(body: dict, transport: Transport, path: str) -> bool:
        """Resolves ``reliable:``, refusing to guarantee delivery twice.

        @param body The raw link mapping.
        @param transport The link's transport.
        @param path Schema path, for the error message.
        @return Whether the framework layers its own delivery guarantee on.
        @throws SchemaShapeError If the value is not a boolean, or a transport
                that already guarantees delivery is asked for reliability.
        """
        if "reliable" not in body:
            return Link.default_reliable(transport)

        reliable = body["reliable"]
        if not isinstance(reliable, bool):
            raise SchemaShapeError(
                path, f"'reliable' must be true or false, got {reliable!r}"
            )

        if reliable and transport.guarantees_delivery:
            raise SchemaShapeError(
                path,
                f"transport '{transport.value}' already delivers every frame in "
                "order, so 'reliable: true' would add a sequence field, a retry "
                "timer and a resend buffer to re-guarantee what the transport has "
                "already guaranteed. Drop the 'reliable' key (it defaults to false "
                "here); if the link really can lose frames, it is not tcp.",
            )
        return reliable

    @staticmethod
    def __resolve_retry_policy(
        body: dict, reliable: bool, path: str
    ) -> "tuple[Optional[int], Optional[int]]":
        """Resolves ``retries``/``buffer_depth``, which only a reliable link has.

        @param body The raw link mapping.
        @param reliable Whether the link is reliable.
        @param path Schema path, for the error message.
        @return The retry count and buffer depth, or ``(None, None)``.
        @throws SchemaShapeError If either key is declared on a non-reliable
                link, or is not a positive integer.
        """
        if not reliable:
            declared = [key for key in _RELIABLE_ONLY if key in body]
            if declared:
                raise SchemaShapeError(
                    path,
                    f"{' and '.join(repr(key) for key in declared)} "
                    f"{'describes' if len(declared) == 1 else 'describe'} how a "
                    "reliable link resends, but this link is not reliable - nothing "
                    "is ever resent, so the value would be silently ignored. Either "
                    "set 'reliable: true', or drop "
                    f"{'the key' if len(declared) == 1 else 'the keys'}.",
                )
            return None, None

        return (
            Link.__parse_count(body, "retries", _DEFAULT_RETRIES, path),
            Link.__parse_count(body, "buffer_depth", _DEFAULT_BUFFER_DEPTH, path),
        )

    @staticmethod
    def __parse_count(body: dict, field: str, fallback: int, path: str) -> int:
        """Validates one positive-integer field, or supplies its default.

        @param body The raw link mapping.
        @param field Which key to read.
        @param fallback The value when the key is absent.
        @param path Schema path, for the error message.
        @return The count.
        @throws SchemaShapeError If the value is not a positive integer.
        """
        if field not in body:
            return fallback

        raw = body[field]
        # bool is an int subclass, and `retries: true` is a mistake worth naming.
        if isinstance(raw, bool) or not isinstance(raw, int):
            raise SchemaShapeError(path, f"'{field}' must be an integer, got {raw!r}")
        if raw < 1:
            raise SchemaShapeError(
                path,
                f"'{field}' must be at least 1, got {raw}. A reliable link that may "
                "not resend, or may hold no frame in flight, cannot deliver "
                "reliably; use 'reliable: false' if that is what you meant.",
            )
        return raw
