// SPDX-License-Identifier: BSL-1.1
/**
* @file task_unpack_adapter.hpp
*
* @brief Adapts a native-constructor task so it can be built from a raw wire
*        payload, bridging the external channel's `buffer_view` to a task's
*        typed constructor.
*
* @ingroup etask_core etask::core
*
* ## The problem it solves
*
* A schema-generated task has a *native-typed* constructor, e.g.
* `spin(std::uint8_t duty, context& ctx)`. But a task arrives over the wire as
* an opaque `payload`, and `task_manager`/`dispatch_factory` construct a task
* from exactly one `etools::memory::buffer_view` (the request's argument bytes).
* A native-ctor task is not constructible from a `buffer_view`, so the factory
* silently skips it (its branch is SFINAE-disabled) and registration fails.
*
* `task_unpack_adapter<Task, Args...>` is the missing link: it *is* a `Task`
* (public inheritance), *is* constructible from a `buffer_view`, and does the
* one thing in between - `unpack<Args...>()` the payload into the task's native
* argument types and forward them to `Task`'s constructor. It is registered in
* the manager's task list in place of the bare task.
*
* ## Why it is free
*
* The adapter adds no members and no virtuals; it is a `Task` with one extra
* constructor. Unpacking is a compile-time-shaped `eser::flat` deserialize and a
* tuple forward through an `index_sequence`, all inlined away - the emitted code
* is the same as if the factory had called the native constructor directly. It
* inherits `Task::uid` (so the uid extractor still finds it) and is-a `Task`
* is-a `task<...>` (so the factory's `is_base_of` checks are unchanged).
*
* ## Scope injection
*
* A task that lives in a scope takes its scope's `context&` as the last
* constructor argument. There is no context to hand in at the `buffer_view`
* call site, so `scoped_task_unpack_adapter` binds the scope's (static-storage)
* instance as a C++17 reference non-type template parameter and forwards it
* after the unpacked arguments - keeping scope access fully static.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-08-03
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_TASK_UNPACK_ADAPTER_HPP_
#define ETASK_CORE_TASK_UNPACK_ADAPTER_HPP_
#include <etools/memory/buffer_view.hpp>
#include <tuple>
#include <type_traits>
#include <utility>

namespace etask::core {

    /**
    * @class task_unpack_adapter
    *
    * @brief Constructs `Task(Args...)` from a wire payload by unpacking it.
    *
    * Register this in the task list in place of a bare native-ctor task with no
    * scope. See the file docs for the rationale.
    *
    * @tparam Task The concrete task type, with constructor `Task(Args...)`.
    * @tparam Args The native argument types, in wire order (the task's params).
    */
    template<typename Task, typename... Args>
    class task_unpack_adapter : public Task {
        static_assert(
            (std::is_default_constructible_v<Args> && ...),
            "task_unpack_adapter needs each unpacked argument type to be default-constructible: "
            "it is the value used when the payload is too short to unpack. Every schema "
            "parameter type satisfies this."
        );

    public:
        /**
        * @brief Build the task from a raw payload.
        *
        * `unpack<Args...>()` recovers the typed arguments; on a payload too short
        * to unpack, value-initialized arguments are used instead (a well-formed
        * fallback rather than undefined behavior - the external channel is
        * expected to reject an undersized payload before it reaches here).
        *
        * @param payload The request's argument bytes (`request::args()`).
        */
        explicit task_unpack_adapter(etools::memory::buffer_view payload)
            : task_unpack_adapter(
                  payload.template unpack<Args...>().value_or(std::tuple<Args...>{}),
                  std::index_sequence_for<Args...>{})
        {
        }

    private:
        template<std::size_t... I>
        task_unpack_adapter(std::tuple<Args...>&& args, std::index_sequence<I...>)
            : Task(std::get<I>(std::move(args))...)
        {
        }
    };

    /**
    * @class scoped_task_unpack_adapter
    *
    * @brief Constructs `Task(Args..., decltype(Scope))` from a wire payload,
    *        injecting the scope's context after the unpacked arguments.
    *
    * Register this in the task list in place of a bare native-ctor task that
    * belongs to a scope.
    *
    * @tparam Task  The concrete task type, with constructor `Task(Args..., Scope&)`.
    * @tparam Scope A reference (non-type template parameter) to the scope's
    *               static-storage `context` instance, forwarded as the last
    *               constructor argument.
    * @tparam Args  The native argument types, in wire order (the task's params).
    */
    template<typename Task, auto& Scope, typename... Args>
    class scoped_task_unpack_adapter : public Task {
        static_assert(
            (std::is_default_constructible_v<Args> && ...),
            "scoped_task_unpack_adapter needs each unpacked argument type to be "
            "default-constructible (the payload-too-short fallback). Every schema "
            "parameter type satisfies this."
        );

    public:
        /// @copydoc task_unpack_adapter::task_unpack_adapter
        explicit scoped_task_unpack_adapter(etools::memory::buffer_view payload)
            : scoped_task_unpack_adapter(
                  payload.template unpack<Args...>().value_or(std::tuple<Args...>{}),
                  std::index_sequence_for<Args...>{})
        {
        }

    private:
        template<std::size_t... I>
        scoped_task_unpack_adapter(std::tuple<Args...>&& args, std::index_sequence<I...>)
            : Task(std::get<I>(std::move(args))..., Scope)
        {
        }
    };

} // namespace etask::core

#endif // ETASK_CORE_TASK_UNPACK_ADAPTER_HPP_
