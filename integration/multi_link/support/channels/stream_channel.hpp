/**
* @file stream_channel.hpp
*
* @brief A byte-stream transport for one link, over a POSIX file descriptor.
*
* @note User-owned support code. The schema describes what a link *guarantees*;
*       it deliberately says nothing about which socket, port or pins carry it,
*       so the transport object lives here and is handed to the channel in
*       config/wiring.hpp.
*
* ## Why a file descriptor rather than a UART or a TCP socket type
*
* This project's subject is the per-link machinery - frame sizing, the `carries()`
* allowlist, the fingerprint handshake - none of which is a property of the
* medium. A descriptor is the smallest thing that carries bytes both ways and can
* be driven by a host test: `verify.py` hands each link one end of a socket pair
* and speaks the other. The same code compiles for the board, where the
* descriptor comes from a real serial port or an lwIP socket instead.
*
* Two links therefore differ here only in which descriptor they hold, which is
* the point: the *policy* difference between them is entirely the schema's, and
* if any of it had to be restated in the transport the generator would not be
* carrying its weight.
*
* ## Framing
*
* Fixed-size records, no delimiters. Every type this channel carries -
* `request_packet_t`, `reply_packet_t`, and the 14-byte handshake preamble - is a
* packed, trivially copyable struct of compile-time known size, and both peers
* are generated from one schema, so both agree on that size before the first
* byte moves. A length prefix would only re-send a number both ends already
* have, and a delimiter would need escaping in payloads that are arbitrary
* bytes.
*
* The consequence to respect is that reads are *record*-granular: a partial
* record is not an error but a not-yet, so @ref do_try_receive buffers what
* arrived and reports nothing until a whole record is in hand. A stream socket
* is free to split any write, and a transport that treated a short read as a
* failed frame would fail intermittently under exactly the load this project is
* meant to test.
*/
#ifndef SUPPORT_CHANNELS_STREAM_CHANNEL_HPP_
#define SUPPORT_CHANNELS_STREAM_CHANNEL_HPP_
#include <ecomm/channels/send_result.hpp>
#include <ecomm/protocol/packet.hpp>
#include <ecomm/protocol/validator.hpp>
#include <cstddef>
#include <cstring>
#include <cstdint>
#include <optional>
#include <type_traits>

namespace support::channels {

    /**
    * @brief Whether a record is an `ecomm` packet, and so has a checksum field.
    *
    * The distinction this transport turns on. Everything it carries is a packed
    * wire struct, but only a real packet has a header a `validator` can seal or
    * check; the handshake preamble is fourteen frozen bytes with no header at
    * all. `validator`'s primary template is deliberately incomplete, so asking
    * it about the preamble is a hard error rather than a substitution failure -
    * which is why this is a trait tested with `if constexpr` rather than an
    * overload left to SFINAE.
    *
    * @tparam T The record type in question.
    */
    template<typename T>
    struct is_packet : std::false_type {};

    /// @brief The specialization that recognises a packet. @see is_packet
    template<
        std::size_t PacketSize,
        ecomm::protocol::topology Topology,
        typename SequencePolicy,
        typename ChecksumPolicy>
    struct is_packet<ecomm::protocol::packet<PacketSize, Topology, SequencePolicy, ChecksumPolicy>>
        : std::true_type {};

    /// @brief Shorthand for @ref is_packet.
    template<typename T>
    inline constexpr bool is_packet_v = is_packet<T>::value;

    /**
    * @class stream_channel
    *
    * @brief An `ecomm` channel that reads and writes fixed-size records on a
    *        file descriptor.
    *
    * Satisfies the `Hub` role `etask::core::channels::external_channel` expects:
    * `send(T&)` and `try_receive<T>()`, both templated on the record type, so one
    * instance carries this link's requests, its replies and its handshake
    * preamble without being told about any of them.
    *
    * ## Why this does not derive from `ecomm::channels::channel`
    *
    * The CRTP base would be the obvious thing to reuse, and it is what a
    * packet-only transport should use. It cannot serve here, because
    * `external_channel::begin_handshake()` sends the 14-byte preamble through
    * this same object - and `channel::send` unconditionally instantiates
    * `ecomm::protocol::validator<Packet>` to seal a checksum, a template
    * deliberately left incomplete for anything that is not an
    * `ecomm::protocol::packet`. The preamble is deliberately *not* a packet
    * (that is the entire reason it exists), so the two requirements are in
    * direct conflict and the base cannot satisfy both.
    *
    * Implementing the two-method role directly is the smaller compromise. The
    * checksum the base would have applied is not dropped: @ref send and
    * @ref try_receive still seal and verify through `validator`, but only for
    * types that *have* one, which is what the base could not express. `bench`'s
    * crc16 is therefore still computed on the way out and checked on the way in -
    * `protocol::reply` builds the header but leaves the FCS to the transport, so
    * skipping this would put a permanently wrong checksum on every reply.
    *
    * Non-owning of the descriptor: whoever opened it closes it. A channel that
    * closed the fd it was handed could not be given one end of a socket pair the
    * test harness also holds.
    */
    class stream_channel {
    public:
        /**
        * @brief Binds this channel to an already-open descriptor.
        *
        * @param fd A readable and writable descriptor, expected to be in
        *        non-blocking mode. Not owned and not closed by this channel; it
        *        must outlive it.
        */
        explicit stream_channel(int fd) noexcept : _fd{fd} {}

        /**
        * @brief Points this channel at a descriptor after construction.
        *
        * Needed because the channels in config/wiring.hpp are composition-root
        * globals, constructed before `main` runs and therefore before any port
        * has been opened. Binding at construction instead would mean opening
        * hardware during static initialisation, which is the ordering hazard the
        * generated context tree goes out of its way to avoid.
        *
        * @param fd A readable and writable descriptor, not owned. Replaces
        *        whatever this channel held; any partially reassembled record from
        *        the previous descriptor is discarded, since it cannot be
        *        completed from a different stream.
        */
        void bind(int fd) noexcept
        {
            _fd = fd;
            _held = 0;
        }

        /**
        * @brief Writes one record, whole, sealing its checksum if it has one.
        *
        * @tparam Record A trivially copyable, packed wire type.
        * @param record The value to write. Taken by non-const reference because
        *        sealing writes the FCS field back into it, exactly as
        *        `ecomm::channels::channel::send` does.
        * @return `ok` once the bytes are away. A descriptor that refused them
        *         reports `timeout`, which is `send_result`'s only failure
        *         enumerator - it names an unacknowledged frame rather than a
        *         write error, but the caller's recourse is the same and
        *         inventing a distinction the enum does not carry would be worse.
        */
        template<typename Record>
        ecomm::channels::send_result send(Record& record) noexcept
        {
            if constexpr (is_packet_v<Record>) ecomm::protocol::validator<Record>{}.seal(record);

            return write_all(reinterpret_cast<const std::byte*>(&record), sizeof(Record))
                ? ecomm::channels::send_result::ok
                : ecomm::channels::send_result::timeout;
        }

        /**
        * @brief Reads one record if a whole, valid one has arrived.
        *
        * Buffers across calls, because a stream may deliver a record in pieces
        * and a caller polling each tick must not lose the pieces that arrived
        * early. A disengaged result is "not yet", not an error.
        *
        * @tparam Record A trivially copyable, packed wire type. Named explicitly
        *         at the call site - there is no argument to deduce it from.
        * @return The record, or nothing if one has not fully arrived or failed
        *         its checksum.
        */
        template<typename Record>
        [[nodiscard]] std::optional<Record> try_receive() noexcept
        {
            static_assert(sizeof(Record) <= capacity,
                "stream_channel's reassembly buffer is smaller than this record; "
                "raise `capacity` to the largest packet the schema generates.");

            if (not fill(sizeof(Record))) return std::nullopt;

            Record record{};
            std::memcpy(&record, _buffer, sizeof(Record));
            consume(sizeof(Record));

            // A corrupt frame is dropped rather than reported: the layer above
            // polls and has no error channel, and a link that answered a bad
            // checksum with an error frame would be answering a peer it cannot
            // trust the address of.
            if constexpr (is_packet_v<Record>) {
                if (not ecomm::protocol::validator<Record>{}.is_valid(record)) return std::nullopt;
            }
            return record;
        }

        /**
        * @brief Reads the fixed-size handshake preamble, if one has arrived.
        *
        * Separate from @ref do_try_receive because the preamble is not a packet
        * and the channel above does not poll for it: `external_channel` exposes
        * `accept_handshake(const std::byte*)` and leaves getting those bytes to
        * whoever owns the receive path, which on a stream transport is this
        * object. Reading it through the same buffer as packets is what keeps the
        * two in order - the preamble precedes task traffic on the wire, and a
        * second buffer could reorder them.
        *
        * @param out Receives `length` bytes, only when true is returned.
        * @param length The preamble's frozen size, from
        *        `etask::core::protocol::preamble::size`. Passed rather than
        *        hard-coded so this file states no wire constant of its own.
        * @return Whether a whole preamble was produced.
        */
        bool try_receive_raw(std::byte* out, std::size_t length) noexcept
        {
            if (length > capacity or not fill(length)) return false;

            std::memcpy(out, _buffer, length);
            consume(length);
            return true;
        }

    private:
        /**
        * @brief The reassembly buffer's size.
        *
        * Sized by hand rather than by the schema because this class is
        * deliberately not templated on a link: one buffer serves both links, and
        * 256 bytes clears the largest frame either generates by a wide margin
        * while staying trivial on an ESP32. The `static_assert` in
        * @ref do_try_receive is what makes the margin checked rather than hoped
        * for - a schema that outgrows this fails to compile.
        */
        static constexpr std::size_t capacity = 256;

        /**
        * @brief Reads until the buffer holds at least `needed` bytes.
        *
        * @param needed How many bytes the caller is about to take.
        * @return Whether the buffer now holds them.
        */
        bool fill(std::size_t needed) noexcept;

        /**
        * @brief Drops the first `count` buffered bytes, keeping the rest.
        *
        * The remainder is shifted down rather than tracked with a read offset:
        * records are consumed whole and promptly, so the buffer is nearly always
        * empty afterwards and a memmove of nothing costs nothing - while an
        * offset would add a wrap case to every read for no measurable gain.
        *
        * @param count Bytes to discard from the front.
        */
        void consume(std::size_t count) noexcept;

        /**
        * @brief Writes a whole buffer, retrying a partial write.
        *
        * @param bytes First byte to write.
        * @param length How many.
        * @return Whether all of them were written.
        */
        bool write_all(const std::byte* bytes, std::size_t length) noexcept;

        /// @brief The descriptor this link speaks over. Not owned.
        int _fd;

        /// @brief Bytes received but not yet consumed by a whole record.
        std::byte _buffer[capacity]{};

        /// @brief How many of @ref _buffer are live.
        std::size_t _held{0};
    };

} // namespace support::channels

#endif // SUPPORT_CHANNELS_STREAM_CHANNEL_HPP_
