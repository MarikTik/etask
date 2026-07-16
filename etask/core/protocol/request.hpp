// SPDX-License-Identifier: MIT
/**
* @file request.hpp
*
* @brief A structured, parsed view over an incoming wire packet's payload.
*
* @ingroup etask_core etask::core::protocol
*
* `ecomm::protocol::packet` gives you a raw `std::byte payload[]`; `request`
* is the etask-defined structured accessor over that payload, in the same
* spirit as `ecomm::protocol::packet_header` being a structured accessor over
* the raw protocol byte - parse once at the boundary, work with named fields
* everywhere else.
*
* ## Topology: `request` itself is partially specialized, not aliased
*
* Whether a request carries a `sender_id` depends entirely on
* `Packet::header_t::has_node_ids`. `request<Packet, TaskUid>` is the real
* class template, partially specialized on a defaulted `bool HasNodeIds` that
* mirrors `Packet::header_t::has_node_ids`: `request<Packet, TaskUid, true>`
* has `sender_id()`, `request<Packet, TaskUid, false>` does not. Callers
* almost never name the third parameter - it defaults from `Packet` - but its
* presence is what keeps `request` a genuine, single, specializable template
* name usable in other templates (trait matching, template-template
* parameters, ...), which an alias-to-two-unrelated-classes could not
* support: alias templates cannot themselves be the pattern in a partial
* specialization. `addressed_request_t`/`unaddressed_request_t` below are
* secondary convenience aliases *of* `request<...>`, for when the topology is
* already known and spelling out the third argument would be noise. See
* `reply.hpp` for the mirror-image design on the outbound side.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-07-13
*
* @copyright
* MIT License
* Copyright (c) 2026 Mark Tikhonov
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_PROTOCOL_REQUEST_HPP_
#define ETASK_CORE_PROTOCOL_REQUEST_HPP_
#include "directive.hpp"
#include "../completion_reason.hpp"
#include <etools/memory/buffer_view.hpp>
#include <type_traits>
#include <cstdint>
#include <cstddef>

namespace etask::core::protocol {

    namespace detail {

        /**
        * @class request_base
        *
        * @brief Topology-independent request parsing, shared by both
        *        specializations of `request`.
        *
        * Payload parsing only - implemented once here so neither
        * specialization duplicates it. See `request<Packet, TaskUid, true>`
        * and `request<Packet, TaskUid, false>` below for the full wire
        * schematic, including where topology-dependent header fields fit in.
        *
        * @warning Holds a reference to the `Packet` it was constructed from;
        *          the packet must outlive every request parsed from it.
        */
        template<typename Packet, typename TaskUid>
        class request_base {
        public:
            static_assert(
                Packet::payload_size >= sizeof(std::byte) + sizeof(TaskUid),
                "Packet's payload is too small to carry a directive and a TaskUid."
            );

            explicit request_base(const Packet& packet) noexcept;

            /** @brief Which task_manager operation this request asks for. */
            [[nodiscard]] directive::operation command() const noexcept;

            /** @brief The target task's uid. */
            [[nodiscard]] TaskUid uid() const noexcept;

            /**
            * @brief Why to force-complete the task. Only meaningful when
            *        `command() == directive::complete_task`.
            */
            [[nodiscard]] completion_reason reason() const noexcept;

            /**
            * @brief The task constructor argument bytes. Only meaningful when
            *        `command() == directive::register_task`.
            */
            [[nodiscard]] etools::memory::buffer_view args() const noexcept;

        protected:
            const Packet& _packet;
        };

    } // namespace detail

    /**
    * @brief Primary template, intentionally incomplete.
    *
    * `HasNodeIds` always resolves to one of the two specializations below via
    * its default; there is no third state. See the two specializations for
    * the actual class bodies.
    */
    template<typename Packet, typename TaskUid, bool HasNodeIds = Packet::header_t::has_node_ids>
    class request;

    /**
    * @brief `request` specialization for a `Packet` whose topology carries a `sender_id`
    *        (`Packet::header_t::has_node_ids == true`, i.e. `topology::network`).
    *
    * Wire picture:
    * ```
    * Packet::header  : ... | sender_id (1B) | ...   (topology-owned; see ecomm::protocol::packet_header)
    * Packet::payload :
    *   +------------------+-----------------------+-------------------------------+
    *   | packed      (1B) | uid  (sizeof(TaskUid)) | tail (command-specific, $)    |
    *   +------------------+-----------------------+-------------------------------+
    * packed : directive - operation (high 2 bits) | completion_reason (low 6 bits), see directive.hpp
    * uid    : TaskUid, raw bytes (memcpy, not a serialized form)
    * ($) tail, by command:
    *     register_task                             : remaining bytes -> buffer_view,
    *         forwarded as-is to the task constructor. Unpacking this into typed,
    *         per-task constructor arguments is future work; today's task_manager
    *         already expects exactly one buffer_view argument, so this is not a
    *         placeholder shortcut so much as today's actual contract.
    *     pause_task / resume_task / complete_task   : empty (complete_task's reason
    *         already travels packed into the `packed` byte above).
    * ```
    */
    template<typename Packet, typename TaskUid>
    class request<Packet, TaskUid, true> : public detail::request_base<Packet, TaskUid> {
        static_assert(Packet::header_t::has_node_ids,
            "request<Packet, TaskUid, true> instantiated for a Packet without node ids; "
            "let the third argument default instead of supplying it explicitly.");
    public:
        using detail::request_base<Packet, TaskUid>::request_base;

        /** @brief The originating device's id, read from `Packet::header.sender_id`. */
        [[nodiscard]] std::uint8_t sender_id() const noexcept;
    };

    /**
    * @brief `request` specialization for a `Packet` whose topology has no
    *        per-message addressing (`Packet::header_t::has_node_ids == false`,
    *        i.e. `topology::point_to_point`).
    *
    * Wire picture:
    * ```
    * Packet::header  : no addressing fields - a point-to-point link has exactly one peer.
    * Packet::payload :
    *   +------------------+-----------------------+-------------------------------+
    *   | packed      (1B) | uid  (sizeof(TaskUid)) | tail (command-specific, $)    |
    *   +------------------+-----------------------+-------------------------------+
    * packed : directive - operation (high 2 bits) | completion_reason (low 6 bits), see directive.hpp
    * uid    : TaskUid, raw bytes (memcpy, not a serialized form)
    * ($) tail, by command:
    *     register_task                             : remaining bytes -> buffer_view,
    *         forwarded as-is to the task constructor (today's task_manager contract).
    *     pause_task / resume_task / complete_task   : empty (complete_task's reason
    *         already travels packed into the `packed` byte above).
    * ```
    *
    * No `sender_id()` anywhere in this class: there is nothing to report.
    * Callers generic over `Packet` must branch on
    * `Packet::header_t::has_node_ids` (typically via `if constexpr`) before
    * calling `sender_id()` - see `external_channel` for the pattern, and
    * `no_addressing_id` for the point-to-point substitute value.
    */
    template<typename Packet, typename TaskUid>
    class request<Packet, TaskUid, false> : public detail::request_base<Packet, TaskUid> {
        static_assert(not Packet::header_t::has_node_ids,
            "request<Packet, TaskUid, false> instantiated for a Packet with node ids; "
            "let the third argument default instead of supplying it explicitly.");
    public:
        using detail::request_base<Packet, TaskUid>::request_base;
    };

    /** @brief Convenience alias for the addressed (`network`-topology) specialization. */
    template<typename Packet, typename TaskUid>
    using addressed_request_t = request<Packet, TaskUid, true>;

    /** @brief Convenience alias for the unaddressed (`point_to_point`-topology) specialization. */
    template<typename Packet, typename TaskUid>
    using unaddressed_request_t = request<Packet, TaskUid, false>;

} // namespace etask::core::protocol

#include "request.tpp"
#endif // ETASK_CORE_PROTOCOL_REQUEST_HPP_
