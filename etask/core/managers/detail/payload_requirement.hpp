// SPDX-License-Identifier: MIT
/**
* @file payload_requirement.hpp
*
* @brief How many payload bytes a project's tasks need on the wire.
*
* @ingroup etask_core etask::core::managers
*
* ## The invariant this exists to check
*
* A packet's payload capacity is fixed at compile time by its type; how many
* bytes a task's arguments occupy is fixed at compile time by the schema. If the
* first is smaller than the second, every request for that task reads argument
* bytes the peer never sent - and nothing catches it, because the deserializer's
* length check is handed the packet's *capacity*, which is always large enough
* to satisfy it. The task is constructed from zero-fill and runs.
*
* That is a hand-maintained invariant across two files (`config/protocol.hpp`
* picks the size, the schema decides the need), which is the kind that is wrong
* eventually. These traits let the meeting point assert it instead, so an
* undersized packet is a build error naming the offending task rather than a
* silent misfire in the air.
*
* ## Why it lives on the manager
*
* The check needs the schema and the packet type together, and the only thing
* that sees both is the channel - which knows its `Packet` and holds a `Manager`
* built from the generated task list. So the manager computes what its own tasks
* need, and the channel compares that against what its packet carries.
*
* Nothing here needs the generator: a generated task already declares
* `using params = etools::meta::typelist<Args...>`, which is precisely the
* argument list whose serialized size this measures.
*
* @note Internal. Nothing outside `etask::core::managers` should name these.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-08-28
*
* @copyright
* MIT License
* Copyright (c) 2026 Mark Tikhonov
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_MANAGERS_DETAIL_PAYLOAD_REQUIREMENT_HPP_
#define ETASK_CORE_MANAGERS_DETAIL_PAYLOAD_REQUIREMENT_HPP_
#include "registered_task.hpp"
#include <eser/flat/size.hpp>
#include <etools/meta/typelist.hpp>
#include <etools/factories/utils/capacity.hpp>
#include <cstddef>

namespace etask::core::managers::detail {

    /**
    * @struct params_size
    *
    * @brief Serialized size of a task's declared constructor parameters.
    *
    * Exists to unpack the `params` typelist into `serialized_size_of`'s
    * parameter pack.
    *
    * @tparam Params A task's `params` typelist.
    */
    template<typename Params>
    struct params_size;

    /**
    * @brief Bytes a pack of arguments occupies on the wire.
    *
    * `if constexpr` rather than a ternary: `serialized_size_of` has no
    * zero-argument form, and both arms of a ternary would be instantiated.
    *
    * @tparam Args The argument types, in wire order.
    * @return Their total serialized size; zero for none.
    */
    template<typename... Args>
    [[nodiscard]] constexpr std::size_t size_of_args() noexcept
    {
        if constexpr (sizeof...(Args) == 0)
            return 0;
        else
            return eser::flat::serialized_size_of<Args...>();
    }

    /// @brief The general case. @see params_size
    template<typename... Args>
    struct params_size<etools::meta::typelist<Args...>> {
        /// @brief Bytes these arguments occupy on the wire; zero for none.
        static constexpr std::size_t value = size_of_args<Args...>();
    };

    /**
    * @var task_payload_need_v
    *
    * @brief Payload bytes one task's arguments need, or zero if it takes none
    *        from the wire.
    *
    * A task that declares no `params` is either argument-free or reachable only
    * in-process (`internal_channel::register_task` with the caller's own typed
    * arguments). Either way it asks nothing of the payload, so it constrains
    * nothing here.
    *
    * @tparam T A manager pack element: a bare task or a `capacity<Task, N>` tag.
    */
    template<typename T, typename = void>
    inline constexpr std::size_t task_payload_need_v = 0;

    /// @brief A task that declares its wire parameters. @see task_payload_need_v
    template<typename T>
    inline constexpr std::size_t task_payload_need_v<
        T,
        std::enable_if_t<declares_params_v<typename etools::factories::utils::as_capacity_t<T>::type>>>
        = params_size<typename etools::factories::utils::as_capacity_t<T>::type::params>::value;

    /**
    * @brief The larger of two sizes.
    *
    * `std::max` is not usable in a fold expression, which needs a binary
    * operator; this is the operation a fold cannot spell.
    *
    * @param a One size.
    * @param b The other.
    * @return The larger.
    */
    [[nodiscard]] constexpr std::size_t larger(std::size_t a, std::size_t b) noexcept
    {
        return a > b ? a : b;
    }

    /**
    * @struct max_params_size
    *
    * @brief The largest argument payload across a manager's whole task pack.
    *
    * The figure a request packet must be able to carry, over and above the
    * directive byte and the uid. A fold would be the natural spelling, but the
    * operation is `max`, which is not an operator - so the recursion is written
    * out.
    *
    * @tparam Tasks A manager's task pack.
    */
    template<typename... Tasks>
    struct max_params_size;

    /// @brief An empty pack asks nothing of the payload. @see max_params_size
    template<>
    struct max_params_size<> {
        static constexpr std::size_t value = 0;
    };

    /// @brief This task against the rest. @see max_params_size
    template<typename Head, typename... Tail>
    struct max_params_size<Head, Tail...> {
        static constexpr std::size_t value =
            larger(task_payload_need_v<Head>, max_params_size<Tail...>::value);
    };

    /**
    * @var max_params_size_v
    *
    * @brief The largest argument payload across a manager's whole task pack.
    * @tparam Tasks A manager's task pack.
    */
    template<typename... Tasks>
    inline constexpr std::size_t max_params_size_v = max_params_size<Tasks...>::value;

} // namespace etask::core::managers::detail

#endif // ETASK_CORE_MANAGERS_DETAIL_PAYLOAD_REQUIREMENT_HPP_
