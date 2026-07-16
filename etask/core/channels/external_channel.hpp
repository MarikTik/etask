// SPDX-License-Identifier: BSL-1.1
/**
* @file external_channel.hpp
*
* @brief Declares the external communication channel bridging wire packets to
*        a task manager.
*
* @ingroup etask_core etask::core::channels
*
* `external_channel` is the counterpart to `internal_channel`: where
* `internal_channel` serves tasks initiated from within the same device,
* `external_channel` serves tasks requested by another device over the wire,
* via an `ecomm` hub/channel.
*
* ## Dependency injection
*
* Like `internal_channel`, this is core library mechanism, parameterized on
* the concrete types it needs rather than reaching for global names:
*
* - `Packet`  - the concrete `ecomm::protocol::packet<...>` instantiation this
*   channel speaks. Works under both `ecomm::protocol::topology::network` and
*   `topology::point_to_point` - see `protocol::request`/`protocol::reply` for
*   how addressing is handled (or isn't) in each case.
* - `Hub`     - anything exposing `try_receive<Packet>() -> std::optional<Packet>`
*   and `send(Packet&) -> ecomm::protocol::send_result` - an `ecomm::hub<...>`
*   or a single `ecomm::channels::channel<Impl, Packet>` both satisfy this.
* - `Manager` - a `task_manager<...>` instantiation, exactly as for
*   `internal_channel`.
*
* ## Wire payload schema
*
* `ecomm::protocol::packet` imposes no application-layer schema on its
* `payload` (see its own docstring): task ids, commands, and status codes are
* not header fields in the current protocol version. `etask::core::protocol`
* (`request`/`reply`/`directive`) defines and owns that schema; this class
* only orchestrates polling, dispatch, and sending.
*
* @note Unpacking the trailing payload bytes into *typed, per-task* constructor
*       arguments (rather than a single `buffer_view`) is future work; today's
*       `task_manager` already expects exactly one `buffer_view` constructor
*       argument, so forwarding the raw remaining bytes is today's real
*       contract, not a placeholder shortcut. It will need revisiting once
*       tasks gain native-typed constructors.
*
* @see protocol/request.hpp, protocol/reply.hpp for the wire schema.
* @see internal_channel for the analogous system-initiated counterpart.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-07-13
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_CHANNELS_EXTERNAL_CHANNEL_HPP_
#define ETASK_CORE_CHANNELS_EXTERNAL_CHANNEL_HPP_
#include "../channel.hpp"
#include "../status_code.hpp"
#include "../protocol/protocol.hpp"
#include <etools/memory/buffer.hpp>
#include <cstdint>

namespace etask::core::channels {

    namespace protocol = etask::core::protocol;

    /**
    * @class external_channel
    *
    * @brief Channel implementation for tasks requested by another device over the wire.
    *
    * @tparam Packet  A `ecomm::protocol::packet<...>` instantiation. Must be
    *         large enough to carry `protocol::request`/`protocol::reply`'s
    *         minimum payload (see their own static_asserts).
    * @tparam Hub     Anything exposing `try_receive<Packet>()` and `send(Packet&)`.
    *         Injected by reference at construction; not owned.
    * @tparam Manager A `task_manager<...>` instantiation. Injected by reference
    *         at construction; not owned.
    *
    * #### Responsibilities:
    *
    * - Poll `Hub` for inbound packets, parse via `protocol::request`.
    * - Forward decoded requests to the injected task manager.
    * - Encode task results/errors via `protocol::reply` and send via `Hub`.
    */
    template<typename Packet, typename Hub, typename Manager>
    class external_channel : public channel<typename Manager::task_uid_t> {
    public:
        /** @typedef task_uid_t
        * @brief The task identifier type, taken from `Manager::task_uid_t`.
        */
        using task_uid_t = typename Manager::task_uid_t;

        /**
        * @brief Binds this channel to the hub and manager it bridges between.
        * @param hub     Transport this channel polls/sends through. Must outlive
        *        this channel; held by reference, not owned.
        * @param manager The task manager this channel drives. Must outlive
        *        this channel; held by reference, not owned.
        */
        external_channel(Hub& hub, Manager& manager) noexcept;

        /// @brief Deleted copy constructor - an adapter bound to one hub/manager pair.
        external_channel(const external_channel&) = delete;
        /// @brief Deleted copy assignment - see the deleted copy constructor.
        external_channel& operator=(const external_channel&) = delete;
        /// @brief Deleted move constructor - see the deleted copy constructor.
        external_channel(external_channel&&) = delete;
        /// @brief Deleted move assignment - see the deleted copy constructor.
        external_channel& operator=(external_channel&&) = delete;

        /**
        * @brief Delivers a task's result back to the device that requested it.
        *
        * Builds a `protocol::reply` from `uid`/`code`/`result` and sends it
        * via the injected hub, addressed to `initiator_id` when `Packet`'s
        * topology carries addressing at all.
        *
        * @param initiator_id Device id of the original requester (or
        *        `protocol::no_addressing_id` under a point-to-point topology).
        * @param uid Unique identifier of the task that produced the result.
        * @param result Result payload produced by the task (moved from).
        * @param code Status code describing the outcome of the task.
        */
        void on_result(
            std::uint8_t initiator_id,
            task_uid_t uid,
            etools::memory::buffer<>&& result,
            status_code code
        ) override;

        /**
        * @brief Poll the hub for one inbound packet and dispatch it.
        *
        * Parses the packet via `protocol::request` and forwards to the
        * matching `task_manager` operation. On any non-`ok` status, sends an
        * error reply (uid + status code, no result bytes) back to the sender.
        *
        * @note Call this periodically from the application's main loop.
        */
        void update();

    private:
        Hub& _hub;
        Manager& _manager;
    };

} // namespace etask::core::channels

#include "external_channel.tpp"
#endif // ETASK_CORE_CHANNELS_EXTERNAL_CHANNEL_HPP_
