// SPDX-License-Identifier: MIT
/**
* @file instant_task_manager.hpp
*
* @brief Declares `instant_task_manager`, which runs fire-and-forget commands
*        to completion the moment they arrive.
*
* @ingroup etask_core etask::core::managers
*
* ## A manager with nothing to manage
*
* The other two managers exist because their tasks *persist*: they own storage,
* track state, and drive tasks across ticks. An @ref instant_task does none of
* that. It arrives, it runs, it is destroyed - inside the same call.
*
* So this class has no members, no storage, and no lifetime. Every entry point
* is `static`: it is a compile-time dispatch table, not an object. There is
* nothing to construct in the composition root, and the façade holds no
* instance of it.
*
* ## What `dispatch` does
*
* Given a raw uid and the request's argument bytes, it folds over `Tasks...` at
* compile time to find the matching type, constructs it **on the stack** with
* its unpacked arguments, and lets it run. The destructor fires as the call
* returns. No registry slot, no handle, no vtable, no `_tasks` entry, no
* garbage bit, no tick.
*
* ## And nothing comes back
*
* An instant command has no `on_complete`, so there is no result to send and no
* channel involved at all - `dispatch` does not take one. The requester gets no
* reply, not even a success status. That is the contract of the tier, not an
* omission: a caller that needs an answer wants a @ref oneshot_task.
*
* The `status_code` returned here is for the **local caller** - the channel that
* is dispatching - to know whether the command was recognized and run. It never
* reaches the wire.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-08-25
*
* @copyright
* MIT License
* Copyright (c) 2026 Mark Tikhonov
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_MANAGERS_INSTANT_TASK_MANAGER_HPP_
#define ETASK_CORE_MANAGERS_INSTANT_TASK_MANAGER_HPP_
#include "../status_code.hpp"
#include "../tasks/instant_task.hpp"
#include "detail/registry_traits.hpp"
#include <etools/meta/traits.hpp>
#include <etools/meta/typelist.hpp>
#include <etools/factories/utils/capacity.hpp>
#include <array>
#include <type_traits>
#include <utility>

namespace etask::core::managers {

    /**
    * @class instant_task_manager
    *
    * @brief Compile-time dispatcher for the project's @ref instant_task commands.
    *
    * Stateless and never instantiated - every member is `static`. See the file
    * documentation for why a manager for instant tasks has nothing to manage.
    *
    * @tparam Tasks The instant command types this manager dispatches to.
    *
    * @note A `capacity<Task, N>` tag is meaningless here and is rejected: an
    *       instant command reserves no slots, so there is no concurrency to
    *       declare. Commands are listed bare.
    */
    template<typename ...Tasks>
    class instant_task_manager {
    public:
        /**
        * @typedef task_uid_t
        * @brief The command identifier type, taken from the commands' `uid` members.
        */
        using task_uid_t = etools::meta::member_t<detail::uid_extractor, Tasks...>;

    private:
        /// @brief `task_uid_t` normalized to its raw integral form.
        using raw_uid_t = detail::raw_uid_t<task_uid_t>;

    public:
        /**
        * @brief Runs the command identified by `uid`, start to finish, right now.
        *
        * Constructs the matching command on the stack with `args` forwarded to its
        * constructor, then destroys it as this call returns. The command's whole
        * effect happens before `dispatch` comes back.
        *
        * @tparam Args Command constructor argument types.
        *
        * @param uid  Which command to run.
        * @param args Forwarded to that command's constructor.
        *
        * @return `ok` if the command was found and run; `task_unknown` if `uid`
        *         matches no command here, or no constructor accepts `args`. This
        *         status is for the calling channel only - it is never sent to the
        *         requester, which by definition receives no reply.
        */
        template<typename... Args>
        static status_code dispatch(task_uid_t uid, Args&&... args);

        /**
        * @brief Whether this manager owns the command identified by `uid`.
        *
        * The façade's routing predicate. Constant-expression evaluable, so the
        * façade's dispatch costs nothing at runtime.
        *
        * @param raw_uid Raw uid to test.
        * @return `true` if some owned command declares this uid.
        */
        [[nodiscard]] static constexpr bool owns(raw_uid_t raw_uid) noexcept;

    private:
        /**
        * @brief Runs `Task` if its uid matches, reporting whether it did.
        *
        * One arm of the compile-time fold in `dispatch`. Construction happens here,
        * in the arm that matched, so only the selected command is ever built.
        *
        * @tparam Task The candidate command type.
        * @tparam Args Constructor argument types.
        *
        * @param raw_uid The uid being dispatched.
        * @param args    Forwarded to `Task`'s constructor.
        *
        * @return `true` if `Task` matched `raw_uid` and was run.
        */
        template<typename Task, typename... Args>
        static bool run_if_matching(raw_uid_t raw_uid, Args&&... args);

        /// @brief A manager with no commands is certainly a mistake.
        static_assert(sizeof...(Tasks) > 0, "instant_task_manager requires at least one task type.");

        /// @brief Every command must carry a `static constexpr uid`.
        static_assert((etools::meta::has_static_member_variable_uid_v<Tasks> && ...),
            "All tasks must have a static member 'uid' to uniquely identify them.");

        /// @brief Every command type must be distinct.
        static_assert(etools::meta::is_distinct_v<Tasks...>,
            "All task types must be distinct.");

        /// @brief No two commands may share a uid *value*, even as different C++ types.
        static_assert(
            etools::meta::all_distinct_fast(std::array<raw_uid_t, sizeof...(Tasks)>{
                detail::raw_uid_extractor<Tasks>::value...
            }),
            "All tasks must have pairwise-distinct uid values, even if they are different C++ types."
        );

        /**
        * @brief Every command here must actually be an instant task.
        *
        * The tier check that makes the split mean something. A managed task routed
        * here would have its `on_complete` never called and its result never sent -
        * it would simply be constructed and thrown away.
        */
        static_assert((std::is_base_of_v<instant_task, Tasks> && ...),
            "All tasks in an instant_task_manager must derive from instant_task. "
            "A task that produces a result belongs in polled_task_manager "
            "(see oneshot_task); one that can be paused, in stateful_task_manager.");

        /**
        * @brief A `capacity<Task, N>` tag has no meaning for an instant command.
        *
        * Concurrency limits exist to bound *storage*, and an instant command uses
        * none: it lives on the stack for the duration of one call. Two of them can
        * never coexist to contend for anything. Silently accepting the tag would
        * imply a guarantee this manager does not make.
        */
        static_assert(
            (!detail::is_capacity_v<Tasks> && ...),
            "capacity<Task, N> is meaningless for an instant_task: it occupies no "
            "storage and runs to completion within a single call, so there is no "
            "concurrency to limit. List instant commands bare."
        );
    };

} // namespace etask::core::managers

#include "instant_task_manager.tpp"
#endif // ETASK_CORE_MANAGERS_INSTANT_TASK_MANAGER_HPP_
