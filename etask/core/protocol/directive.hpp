// SPDX-License-Identifier: MIT
/**
* @file directive.hpp
*
* @brief Defines `directive`, the etask application-layer command+reason byte
*        carried at the front of a request packet's payload.
*
* @ingroup etask_core etask::core::protocol
*
* `ecomm::protocol::packet` deliberately carries no task-id/status-code/command
* semantics: its `payload` is a raw, uninterpreted `std::byte[]`, and everything
* above the wire protocol is left to the application (see `packet.hpp`'s own
* docstring). etask needs to know, per incoming packet, which task_manager
* operation to invoke and, for `complete_task`, why; `directive` is that
* schema, always occupying `payload[0]`. See `request.hpp`/`reply.hpp` for the
* types that own the full payload layout built on top of this.
*
* Packed byte layout:
* ```
* bit:     7   6      5  4  3  2  1  0
*      +---+---+---+---+---+---+---+---+
*      |  command  |       reason       |
*      +---+---+---+---+---+---+---+---+
*  7..6 : command  (2 bits)  --  directive::operation, 4 values used
*  5..0 : reason   (6 bits)  --  completion_reason; meaningful only when
*                                command == directive::complete_task,
*                                otherwise conventionally 0 (completion_reason::finished)
* ```
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
#ifndef ETASK_CORE_PROTOCOL_DIRECTIVE_HPP_
#define ETASK_CORE_PROTOCOL_DIRECTIVE_HPP_
#include "../completion_reason.hpp"
#include <cstdint>
#include <cstddef>

namespace etask::core::protocol {

    /**
    * @class directive
    *
    * @brief One wire byte: which `task_manager` operation to invoke, plus
    *        (for `complete_task`) why.
    *
    * `operation` has exactly 4 values (2 bits); `completion_reason` is
    * canonically bounded to 6 bits (`completion_reason::max == 0x3F`, see
    * `completion_reason.hpp`) for precisely this reason: the two fit in a
    * single byte with no waste and no separate reason byte on the wire.
    * `reason` is only meaningful when `command() == directive::complete_task`;
    * for every other command it is conventionally `completion_reason::finished`
    * (value `0`), i.e. the low 6 bits are zero.
    */
    class directive {
    public:

        /**
        * @brief Which `task_manager` operation a `directive` requests.
        *
        * Named to mirror the `task_manager`/`internal_channel`/`external_channel`
        * methods it maps to 1:1: `register_task`, `pause_task`, `resume_task`,
        * `complete_task`. Nested (not a free enum) so every value is reached
        * through `directive` - `directive::register_task`, or qualified as
        * `directive::operation` where the type itself is needed.
        */
        enum operation : std::uint8_t {
            register_task = 0,
            pause_task    = 1,
            resume_task   = 2,
            complete_task = 3,
        };

        /**
        * @brief Packs an `operation` and a `completion_reason` into one byte.
        *
        * @pre `is_valid_reason(reason)` (i.e. `reason <= completion_reason::max`).
        *      Violating this silently truncates `reason` - the caller, not this
        *      constructor, is responsible for upholding the 6-bit contract
        *      (enforced for the one caller that matters, `task_manager::complete_task`).
        */
        constexpr directive(operation cmd, completion_reason reason) noexcept;

        /** @brief Wraps an already-packed byte, e.g. read off `Packet::payload[0]`. */
        explicit constexpr directive(std::byte raw) noexcept;

        /** @brief Extracts the `operation` from the high 2 bits. */
        [[nodiscard]] constexpr operation command() const noexcept;

        /** @brief Extracts the `completion_reason` from the low 6 bits. */
        [[nodiscard]] constexpr completion_reason reason() const noexcept;

        /** @brief The packed byte, ready to write to `Packet::payload[0]`. */
        [[nodiscard]] constexpr std::byte raw() const noexcept;

    private:
        static constexpr std::uint8_t reason_bits  = 6;
        static constexpr std::uint8_t command_bits = 8 - reason_bits;

        std::byte _raw;
    };

    /**
    * @brief Placeholder `initiator_id`/`receiver_id` for topologies with no
    *        per-message addressing (`ecomm::protocol::topology::point_to_point`).
    *
    * A point-to-point link has exactly one peer, so there is nothing a real
    * id would distinguish; `task_manager::register_task` still requires a
    * `uint8_t` regardless of topology, so `request`/`external_channel` use
    * this named placeholder rather than a bare, unexplained `0`.
    */
    inline constexpr std::uint8_t no_addressing_id = 0;

} // namespace etask::core::protocol
#include "directive.inl"
#endif // ETASK_CORE_PROTOCOL_DIRECTIVE_HPP_
