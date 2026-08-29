// SPDX-License-Identifier: MIT
/**
* @file preamble.hpp
*
* @brief Defines `preamble`, the fixed 14-byte schema-fingerprint frame two
*        peers exchange before any task traffic.
*
* @ingroup etask_core etask::core::protocol
*
* Every other type in `etask::core::protocol` writes into a
* `ecomm::protocol::packet`'s payload, and so inherits that packet's shape:
* whether the header carries a `receiver_id`, a sequence number, a CRC16 or a
* CRC32 moves every field after it. That is exactly the property that makes a
* packet unusable here.
*
* ## Why the handshake cannot ride in a packet
*
* Two peers generated from different schemas can disagree about the *header
* layout*, not merely about the payload's meaning. A `point_to_point`/no-sequence/
* CRC16 link puts the payload at offset 3; a `network`/sequenced/CRC32 link puts
* it at offset 8. Between those two builds every field misparses, and the frame
* check cannot rescue it because the two ends disagree about where the check
* itself lives. So the message whose entire job is to announce "we disagree
* about frame shape" must not be carried in a frame whose shape is in dispute.
*
* `preamble` is that escape hatch: a byte layout frozen forever, identical for
* every schema, every topology and every checksum policy, so that two peers who
* agree on nothing else still agree on how to read these 14 bytes.
*
* ## Wire layout - FROZEN
*
* ```
* offset size field
*   0     4   magic        "ETSK"  -- resync + "this is an etask preamble"
*   4     1   version      0x01    -- preamble format version, NOT the schema's
*   5     1   reserved     0x00    -- pads the fingerprint to an even offset;
*                                     must be sent as zero, must be ignored on
*                                     receipt so a later version can claim it
*   6     8   fingerprint          -- first 8 bytes of sha256(canonical schema
*                                     string), big-endian
*  ---------
*  14 bytes total
* ```
*
* Magic, version and reserved are single bytes or a byte string, so no
* endianness question arises for them. The fingerprint is carried **big-endian**
* so that a hex dump of the wire reads left-to-right in the same order as the
* sha256 digest it was cut from - the difference between a two-minute diagnosis
* and an afternoon of byte-swapping by hand. It is encoded and decoded with
* explicit shifts, never a `htonl`/`ntohl` or a `memcpy` of the integer, so the
* result is correct by construction on a big- or little-endian host and does not
* depend on a networking header the ESP32 Arduino core does not reliably supply.
*
* ## No checksum, on purpose
*
* The 8-byte hash *is* the integrity check. A preamble corrupted in flight
* fails the fingerprint comparison and is reported as a mismatch, which is the
* correct outcome anyway: a link that cannot deliver 14 clean bytes at connect
* has not earned the right to carry task traffic. Adding a CRC would only let
* the receiver distinguish "corrupt" from "genuinely different schema", and
* both conclusions lead to the same action - refuse the link.
*
* @see handshake.hpp for the per-link state machine that consumes this.
* @see request.hpp, reply.hpp for the ordinary, schema-shaped wire types.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-08-27
*
* @copyright
* MIT License
* Copyright (c) 2026 Mark Tikhonov
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_PROTOCOL_PREAMBLE_HPP_
#define ETASK_CORE_PROTOCOL_PREAMBLE_HPP_
#include "../status_code.hpp"
#include <cstdint>
#include <cstddef>

namespace etask::core::protocol {

    /**
    * @enum preamble_error
    *
    * @brief Which of a preamble's three independent checks failed.
    *
    * `status_code::schema_mismatch` is the single verdict a channel acts on -
    * refuse the link - but it is a poor thing to hand a human staring at a
    * device that has gone quiet. These three causes call for three different
    * fixes, and only the decoder can still tell them apart:
    *
    * - @ref bad_magic - the bytes are not an etask preamble at all. Wrong baud
    *   rate, a peer that speaks some other protocol, or a build predating the
    *   handshake that opened with task traffic.
    * - @ref bad_version - it *is* an etask preamble, from a build whose preamble
    *   format this one does not know. The frozen layout means this should stay
    *   theoretical, which is precisely why it must be reported distinctly rather
    *   than folded into "mismatch".
    * - @ref fingerprint_mismatch - a well-formed preamble from a peer built
    *   against a different schema. The expected case, and the only one the user
    *   fixes by regenerating.
    *
    * @note Corruption in flight surfaces as one of these three rather than as a
    *       category of its own; see the file docstring on why the preamble
    *       carries no checksum.
    */
    enum class preamble_error : std::uint8_t {
        none                 = 0, /**< All checks passed; the fingerprint was recovered. */
        bad_magic            = 1, /**< Bytes 0..3 are not "ETSK". */
        bad_version          = 2, /**< Byte 4 is not a version this build understands. */
        fingerprint_mismatch = 3, /**< Well-formed, but the peer's schema is not ours. */
    };

    /**
    * @class preamble
    *
    * @brief Encodes and decodes the 14-byte schema-fingerprint frame.
    *
    * Stateless: a namespace of `static constexpr` offsets plus @ref encode and
    * @ref decode over a caller-owned `std::byte[size]`. There is no instance to
    * hold because there is nothing to hold - the only datum is the fingerprint,
    * and the caller already has it (see `handshake`, which owns the local one).
    *
    * The offsets are exposed rather than kept private because a peer
    * implementation in another language is written against this table; keeping
    * the constants visible makes this header the single readable statement of
    * the wire format, and lets a test assert the numbers rather than only the
    * round trip.
    */
    class preamble {
    public:
        /// @brief Total wire size, in bytes. Frozen; never varies with a schema.
        static constexpr std::size_t size = 14;

        /// @brief Offset of the 4-byte magic.
        static constexpr std::size_t magic_offset = 0;
        /// @brief Length of the magic, in bytes.
        static constexpr std::size_t magic_size = 4;

        /// @brief Offset of the 1-byte preamble format version.
        static constexpr std::size_t version_offset = 4;

        /**
        * @brief Offset of the reserved pad byte.
        *
        * Sent as zero, ignored on receipt. Not validated: a future version may
        * give it a meaning, and rejecting a non-zero value here would make this
        * build refuse a peer it could otherwise talk to.
        */
        static constexpr std::size_t reserved_offset = 5;

        /// @brief Offset of the big-endian 8-byte fingerprint.
        static constexpr std::size_t fingerprint_offset = 6;
        /// @brief Length of the fingerprint, in bytes.
        static constexpr std::size_t fingerprint_size = 8;

        /**
        * @brief The 4 magic bytes, "ETSK".
        *
        * Serves two jobs: it says these bytes are an etask preamble, and it
        * gives a receiver reading a byte stream something to resynchronise on
        * after garbage - which matters because the peer that most often sends
        * garbage here is one that does not know about preambles at all.
        */
        static constexpr unsigned char magic[magic_size] = {'E', 'T', 'S', 'K'};

        /**
        * @brief Preamble format version this build writes and accepts.
        *
        * Versions the 14-byte *envelope*, not the schema inside it. The schema's
        * identity is entirely the fingerprint; this byte changes only if the
        * envelope's own layout ever must, and the layout is frozen precisely so
        * that it does not.
        */
        static constexpr std::uint8_t version = 0x01;

        /// @brief Value written to the reserved byte.
        static constexpr std::uint8_t reserved = 0x00;

        /**
        * @brief Lays out this peer's preamble into `out`.
        *
        * Writes all @ref size bytes unconditionally, so `out` needs no
        * pre-clearing.
        *
        * @param out         Destination buffer, at least @ref size bytes.
        * @param fingerprint This build's `generated::schema_fingerprint`.
        */
        static void encode(std::byte* out, std::uint64_t fingerprint) noexcept;

        /**
        * @brief Validates a peer's preamble and recovers its fingerprint.
        *
        * Checks magic, then version, then - only if both hold - reads the
        * fingerprint out. The order is what makes the diagnosis usable: a
        * fingerprint recovered from bytes that are not a preamble is a random
        * number, and reporting it as "the peer's schema" sends the reader
        * hunting for a schema that never existed.
        *
        * @param in       Source buffer, at least @ref size bytes.
        * @param expected This build's own fingerprint, to compare against.
        * @param[out] peer_fingerprint Receives the peer's fingerprint when the
        *             magic and version checks pass - including on a mismatch,
        *             where it is the whole point: the caller logs it as the
        *             "actual" against its own "expected". Left untouched when
        *             the bytes are not a recognisable preamble. May be null if
        *             the caller only wants the verdict.
        * @return @ref preamble_error::none on a full match, otherwise which
        *         check failed.
        */
        [[nodiscard]] static preamble_error decode(
            const std::byte* in,
            std::uint64_t expected,
            std::uint64_t* peer_fingerprint = nullptr
        ) noexcept;

        /**
        * @brief Reads the big-endian fingerprint field without validating anything.
        *
        * Exposed for the diagnostic path - dumping what arrived when @ref decode
        * has already said the frame is malformed - and for tests that assert the
        * byte order directly. Ordinary callers want @ref decode.
        *
        * @param in Source buffer, at least @ref size bytes.
        * @return Bytes 6..13 read as a big-endian `uint64_t`.
        */
        [[nodiscard]] static std::uint64_t read_fingerprint(const std::byte* in) noexcept;

        /**
        * @brief Maps a decode result onto the status code a link reports.
        *
        * All three failures collapse to `status_code::schema_mismatch`, because
        * all three lead to the same action - refuse this link's task traffic.
        * The finer-grained @ref preamble_error stays available for the log line;
        * this is what the channel returns.
        *
        * @param error A result from @ref decode.
        * @return `status_code::ok` for @ref preamble_error::none, otherwise
        *         `status_code::schema_mismatch`.
        */
        [[nodiscard]] static constexpr status_code to_status(preamble_error error) noexcept;
    };

} // namespace etask::core::protocol

#include "preamble.inl"
#endif // ETASK_CORE_PROTOCOL_PREAMBLE_HPP_
