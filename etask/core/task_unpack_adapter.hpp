// SPDX-License-Identifier: MIT
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
* call site, so `scoped_task_unpack_adapter` binds the scope through a nullary
* *accessor function* (a function-pointer non-type template parameter) that
* returns the scope reference, and forwards its result after the unpacked
* arguments.
*
* An accessor - rather than a reference non-type template parameter directly -
* is deliberate: in C++17 a reference NTTP argument must name a *variable*, so a
* context that is a **subobject** of a larger object (e.g. a leaf of a single
* composition-root context tree, `root.arm.base`) could not be bound. A
* function can return a reference to any subobject freely, and inlines to
* nothing, so the scope may live wherever the application organizes it - in
* particular as a member of a parent scope's context, giving one root object
* that constructs every context exactly once, in order.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-08-03
*
* @copyright
* MIT License
* Copyright (c) 2025 Mark Tikhonov
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
        * @brief Inherit `Task`'s own constructors, so the adapter adds a way to
        *        build the task without taking one away.
        *
        * A task registered through a manager is reached two ways: from the wire,
        * as a payload (the constructor below), and in-process, with the caller's
        * own typed arguments (`internal_channel::register_task(uid, 1.5f, ctx)`).
        * The manager stores the adapter for *both*, so without this the
        * in-process path would lose the native constructor and fail to register
        * for no reason a caller could see.
        */
        using Task::Task;

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
    * @brief Constructs `Task(Args..., Scope&)` from a wire payload, injecting the
    *        scope returned by `ScopeFn()` after the unpacked arguments.
    *
    * Register this in the task list in place of a bare native-ctor task that
    * belongs to a scope.
    *
    * @tparam Task    The concrete task type, with constructor `Task(Args..., Scope&)`.
    * @tparam ScopeFn A nullary accessor returning the scope reference (e.g.
    *                 `context& (*)()`). Its result is forwarded as the last
    *                 constructor argument. Passed as a function-pointer non-type
    *                 template parameter; see the file docs for why an accessor
    *                 rather than a reference NTTP.
    * @tparam Args    The native argument types, in wire order (the task's params).
    */
    template<typename Task, auto ScopeFn, typename... Args>
    class scoped_task_unpack_adapter : public Task {
        static_assert(
            (std::is_default_constructible_v<Args> && ...),
            "scoped_task_unpack_adapter needs each unpacked argument type to be "
            "default-constructible (the payload-too-short fallback). Every schema "
            "parameter type satisfies this."
        );

    public:
        /// @copydoc task_unpack_adapter::Task::Task
        using Task::Task;

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
            : Task(std::get<I>(std::move(args))..., ScopeFn())
        {
        }
    };

} // namespace etask::core

#endif // ETASK_CORE_TASK_UNPACK_ADAPTER_HPP_
