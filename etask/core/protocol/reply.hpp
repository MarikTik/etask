// SPDX-License-Identifier: MIT
/**
* @file reply.hpp
*
* @brief Builds an outgoing wire packet from a task's uid/status_code/result.
*
* @ingroup etask_core etask::core::protocol
*
* The counterpart to `request`: where `request` parses an incoming packet's
* payload into named fields, `reply` holds named fields and produces a packet.
* There is exactly one reply shape, used both for a concluded task's real
* result and for an immediate manager-API rejection (with an empty result) -
* `task::on_complete` always returns a `buffer<>` regardless of completion
* path, and the wire packet doesn't distinguish "successful" from "error"
* structurally, only via the `status_code` it carries.
*
* ## Topology: `reply` itself is partially specialized, not aliased
*
* Whether a reply needs a `receiver_id` depends entirely on
* `Packet::header_t::has_node_ids` (`ecomm::protocol::topology::network` vs
* `point_to_point`). `reply<Packet, TaskUid>` is the real class template,
* partially specialized on a defaulted `bool HasNodeIds` that mirrors
* `Packet::header_t::has_node_ids`: `reply<Packet, TaskUid, true>` carries
* `receiver_id`, `reply<Packet, TaskUid, false>` does not. Callers almost
* never name the third parameter - it defaults from `Packet` - but its
* presence is what keeps `reply` a genuine, single, specializable template
* name usable in other templates (trait matching, template-template
* parameters, ...), which an alias-to-two-unrelated-classes could not
* support: alias templates cannot themselves be the pattern in a partial
* specialization. `addressed_reply_t`/`unaddressed_reply_t` below are
* secondary convenience aliases *of* `reply<...>`, for when the topology is
* already known and spelling out the third argument would be noise.
*
* The shared parsing/packing logic (`detail::reply_base`) is written once,
* inherited by both specializations, so neither duplicates it.
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
#ifndef ETASK_CORE_PROTOCOL_REPLY_HPP_
#define ETASK_CORE_PROTOCOL_REPLY_HPP_
#include "../status_code.hpp"
#include <etools/memory/buffer_view.hpp>
#include <type_traits>
#include <cstdint>
#include <cstddef>

namespace etask::core::protocol {

    namespace detail {

        /**
        * @class reply_base
        *
        * @brief Topology-independent reply state and payload-packing logic,
        *        shared by both specializations of `reply`.
        *
        * Payload state and packing only - implemented once here so neither
        * specialization duplicates it. See `reply<Packet, TaskUid, true>` and
        * `reply<Packet, TaskUid, false>` below for the full wire schematic,
        * including where topology-dependent header fields fit in.
        *
        * @warning `result` is held as a non-owning `buffer_view`: whatever it
        *          views must outlive this object and any `to_packet()` call.
        *          Construct and consume a reply synchronously, in the same
        *          scope as the `buffer<>` its `result` view came from.
        */
        template<typename Packet, typename TaskUid>
        class reply_base {
        public:
            static_assert(
                Packet::payload_size >= sizeof(TaskUid) + sizeof(status_code),
                "Packet's payload is too small to carry a TaskUid and a status_code."
            );

            reply_base(TaskUid uid, status_code code, etools::memory::buffer_view result) noexcept;

        protected:
            /** @brief Builds the packet with header_type/options set, payload packed; receiver_id (if any) is the derived class's job. */
            [[nodiscard]] Packet build() const noexcept;

            TaskUid _uid;
            status_code _code;
            etools::memory::buffer_view _result;
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
    class reply;

    /**
    * @brief `reply` specialization for a `Packet` whose topology carries a `receiver_id`
    *        (`Packet::header_t::has_node_ids == true`, i.e. `topology::network`).
    *
    * `receiver_id` is captured at construction, alongside `uid`/`code`/`result`
    * - a reply is fully-formed once constructed; `to_packet()` is a pure,
    * argument-less "materialize what this object already represents."
    *
    * Wire picture:
    * ```
    * Packet::header  : ... | receiver_id (1B) | ...   (topology-owned; see ecomm::protocol::packet_header)
    * Packet::payload :
    *   +-----------------------+----------------+-------------------------------+
    *   | uid (sizeof(TaskUid)) | code      (1B) | result (remaining bytes, $)   |
    *   +-----------------------+----------------+-------------------------------+
    * ($) truncated to fit `Packet::payload_size`; empty for an immediate
    *     manager-API rejection (no task ever ran to produce a result).
    * ```
    * `receiver_id` is a separate field owned by `Packet::header`, outside the
    * payload entirely; `to_packet()` writes the constructor-supplied
    * `receiver_id` into it.
    */
    template<typename Packet, typename TaskUid>
    class reply<Packet, TaskUid, true> : public detail::reply_base<Packet, TaskUid> {
        static_assert(Packet::header_t::has_node_ids,
            "reply<Packet, TaskUid, true> instantiated for a Packet without node ids; "
            "let the third argument default instead of supplying it explicitly.");
    public:
        reply(TaskUid uid, status_code code, etools::memory::buffer_view result, std::uint8_t receiver_id) noexcept;

        [[nodiscard]] Packet to_packet() const noexcept;

    private:
        std::uint8_t _receiver_id;
    };

    /**
    * @brief `reply` specialization for a `Packet` whose topology has no
    *        per-message addressing (`Packet::header_t::has_node_ids == false`,
    *        i.e. `topology::point_to_point`).
    *
    * Wire picture:
    * ```
    * Packet::header  : no addressing fields - a point-to-point link has exactly one peer.
    * Packet::payload : 
    *   +-----------------------+----------------+-------------------------------+
    *   | uid (sizeof(TaskUid)) | code      (1B) | result (remaining bytes, $)   |
    *   +-----------------------+----------------+-------------------------------+
    * ($) truncated to fit `Packet::payload_size`; empty for an immediate
    *     manager-API rejection (no task ever ran to produce a result).
    * ```
    *
    * No `receiver_id` anywhere in this class: there is nothing to address.
    */
    template<typename Packet, typename TaskUid>
    class reply<Packet, TaskUid, false> : public detail::reply_base<Packet, TaskUid> {
        static_assert(not Packet::header_t::has_node_ids,
            "reply<Packet, TaskUid, false> instantiated for a Packet with node ids; "
            "let the third argument default instead of supplying it explicitly.");
    public:
        using detail::reply_base<Packet, TaskUid>::reply_base;

        [[nodiscard]] Packet to_packet() const noexcept;
    };

    /** @brief Convenience alias for the addressed (`network`-topology) specialization. */
    template<typename Packet, typename TaskUid>
    using addressed_reply_t = reply<Packet, TaskUid, true>;

    /** @brief Convenience alias for the unaddressed (`point_to_point`-topology) specialization. */
    template<typename Packet, typename TaskUid>
    using unaddressed_reply_t = reply<Packet, TaskUid, false>;

} // namespace etask::core::protocol

#include "reply.tpp"
#endif // ETASK_CORE_PROTOCOL_REPLY_HPP_
