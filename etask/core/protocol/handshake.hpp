// SPDX-License-Identifier: MIT
/**
* @file handshake.hpp
*
* @brief Declares `handshake`, the per-link state that decides whether a peer's
*        schema is ours and therefore whether the link may carry task traffic.
*
* @ingroup etask_core etask::core::protocol
*
* `preamble` is the 14 bytes on the wire; `handshake` is the small amount of
* state a link keeps around them - this build's fingerprint, whether the peer's
* preamble has arrived, and what it said.
*
* ## Transport-agnostic on purpose
*
* This type never reads or writes a byte itself. It takes @ref preamble::size
* bytes that someone else received and hands back @ref preamble::size bytes for
* someone else to send. That is what lets one implementation serve a link that
* is an `ecomm` hub, a raw UART, a socket, or a test harness feeding it arrays -
* and it is why the state machine can be exercised exhaustively without a
* transport at all.
*
* It also carries no timer. A timeout is "the peer never sent one", which is
* indistinguishable from @ref handshake_state::pending from in here; the owner
* of the link is the only party that knows how long is too long, and it says so
* by calling @ref fail. Keeping the clock out of this type keeps it usable from
* an ISR, a poll loop, or an RTOS task without picking a time source for all
* three.
*
* ## Wiring it into a link
*
* Not yet connected to `channels::external_channel` - that is a separate
* change. The intended shape, so the seam is obvious:
*
* - On connect, the channel calls @ref local_preamble and sends those bytes,
*   unframed, before anything else.
* - Every inbound @ref preamble::size bytes that arrive while
*   @ref is_ready is false go to @ref on_peer_preamble instead of to
*   `protocol::request`. This ordering is the load-bearing part: a peer with a
*   different header layout must never have its bytes handed to a parser built
*   for this build's layout.
* - `dispatch` and `complete` return `status_code::schema_mismatch` without
*   touching the manager unless @ref is_ready.
* - A link that goes down resets to @ref handshake_state::pending via
*   @ref reset, because the thing that reconnects may not be the thing that
*   disconnected.
*
* @see preamble.hpp for the wire layout and why it cannot be a packet.
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
#ifndef ETASK_CORE_PROTOCOL_HANDSHAKE_HPP_
#define ETASK_CORE_PROTOCOL_HANDSHAKE_HPP_
#include "preamble.hpp"
#include "../status_code.hpp"
#include <cstdint>
#include <cstddef>

namespace etask::core::protocol {

    /**
    * @enum handshake_state
    *
    * @brief Where one link stands in the fingerprint exchange.
    *
    * Three states, and the asymmetry between the last two is the design:
    * @ref pending is recoverable by waiting, @ref mismatched never is.
    */
    enum class handshake_state : std::uint8_t {
        /**
        * @brief The peer's preamble has not arrived yet. No task traffic.
        *
        * The state a link starts and returns to. Refusing traffic here is not
        * pessimism - a request received before the handshake is a request from
        * a peer whose frame layout is still unknown.
        */
        pending    = 0,

        /**
        * @brief Fingerprints matched. Task traffic is allowed.
        */
        ready      = 1,

        /**
        * @brief The peer failed the check. Task traffic is refused, permanently.
        *
        * Terminal until @ref handshake::reset: retrying cannot help, because
        * nothing about a running peer's schema changes between attempts. The
        * link stays open so both ends can log and be interrogated - the device
        * is meant to remain diagnosable, just not commandable over this link.
        */
        mismatched = 2,
    };

    /**
    * @class handshake
    *
    * @brief Per-link fingerprint exchange state: pending, ready, or mismatched.
    *
    * One instance per link, not per device. A node with three links may be ready
    * on two and mismatched on the third, and that is the intended granularity:
    * one stale peer must not silence a device on the links that are fine.
    *
    * Refusing on mismatch, rather than warning and carrying on, is the entire
    * point of the feature. The fingerprint has just established that this peer's
    * commands would be misread; executing them anyway is strictly worse than not
    * having checked, because now there is a log line saying it was known.
    */
    class handshake {
    public:
        /**
        * @brief Binds this link's state to the fingerprint of this build.
        *
        * @param local_fingerprint This build's `generated::schema_fingerprint`.
        */
        explicit constexpr handshake(std::uint64_t local_fingerprint) noexcept;

        /**
        * @brief Fills `out` with the preamble to send to the peer.
        *
        * Callable in any state, including @ref handshake_state::mismatched: a
        * peer that connects late still needs to be told what it is talking to,
        * and answering with silence turns a diagnosable mismatch into an
        * unexplained dead link.
        *
        * @param out Destination buffer, at least `preamble::size` bytes.
        */
        void local_preamble(std::byte* out) const noexcept;

        /**
        * @brief Consumes the peer's preamble and settles this link's verdict.
        *
        * On success the link becomes @ref handshake_state::ready; on any of the
        * three failures it becomes @ref handshake_state::mismatched and stays
        * there. The peer's fingerprint is retained for the log whenever the
        * bytes were a recognisable preamble at all (see @ref peer_fingerprint).
        *
        * Once mismatched, a second call cannot make the link ready again: a peer
        * that has already been proven wrong does not get to re-assert itself by
        * sending a good preamble afterwards, which would otherwise be a way to
        * talk a device into accepting commands it had already refused. Clearing
        * the verdict is the link owner's decision, through @ref reset.
        *
        * @param in Received bytes, at least `preamble::size` of them.
        * @return `status_code::ok` when the link is ready, otherwise
        *         `status_code::schema_mismatch`. Call @ref last_error for which
        *         check failed.
        */
        [[nodiscard]] status_code on_peer_preamble(const std::byte* in) noexcept;

        /**
        * @brief Declares the handshake failed for a reason outside these bytes.
        *
        * The timeout path: the owner of the link waited long enough and no
        * preamble came, most likely from a build that predates the handshake and
        * opened with task traffic. That peer's schema is unverified, which is the
        * same standing as a peer whose schema is known-wrong, so it lands in the
        * same state.
        *
        * @param error Why it failed; recorded for @ref last_error. Defaults to
        *        @ref preamble_error::bad_magic, the honest description of a peer
        *        that sent something other than a preamble - including nothing.
        * @return `status_code::schema_mismatch`, so a caller can `return`
        *         straight through it.
        */
        status_code fail(preamble_error error = preamble_error::bad_magic) noexcept;

        /**
        * @brief Returns the link to @ref handshake_state::pending.
        *
        * For a reconnect. The peer that comes back may be a different build from
        * the one that dropped - a reflashed device on the same wire - so both a
        * previous `ready` and a previous `mismatched` verdict are discarded, not
        * just the failure.
        */
        void reset() noexcept;

        /** @brief This link's current state. */
        [[nodiscard]] constexpr handshake_state state() const noexcept;

        /** @brief Whether task traffic may flow on this link. */
        [[nodiscard]] constexpr bool is_ready() const noexcept;

        /** @brief This build's fingerprint - the "expected" half of a log line. */
        [[nodiscard]] constexpr std::uint64_t local_fingerprint() const noexcept;

        /**
        * @brief The peer's fingerprint - the "actual" half of a log line.
        *
        * Meaningful once a well-formed preamble has been seen, whether it
        * matched or not. Zero while pending, and zero after a failure that
        * proved the bytes were not a preamble (@ref preamble_error::bad_magic or
        * @ref preamble_error::bad_version), where any value read out of the
        * fingerprint field would be noise dressed up as a schema id.
        */
        [[nodiscard]] constexpr std::uint64_t peer_fingerprint() const noexcept;

        /**
        * @brief Which check failed, for the diagnostic the status code cannot carry.
        *
        * @ref preamble_error::none while pending or ready.
        */
        [[nodiscard]] constexpr preamble_error last_error() const noexcept;

    private:
        std::uint64_t   _local_fingerprint;
        std::uint64_t   _peer_fingerprint = 0;
        handshake_state _state            = handshake_state::pending;
        preamble_error  _last_error       = preamble_error::none;
    };

} // namespace etask::core::protocol

#include "handshake.inl"
#endif // ETASK_CORE_PROTOCOL_HANDSHAKE_HPP_
