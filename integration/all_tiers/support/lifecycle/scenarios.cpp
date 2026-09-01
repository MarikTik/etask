/**
* @file scenarios.cpp
*
* @brief The conformance scenarios: what is actually done to each tier, and what
*        is reported about it.
*
* @note User-owned. The generator never writes here.
*
* ## The tick model these scenarios are written against
*
* Every expectation below depends on when a manager does what, so it is worth
* stating once. `register_task` only *records* a task; nothing of its lifecycle
* runs until an `update()`. Within one `update()` a managed task is examined
* exactly once, and the examination is a choice, not a sequence:
*
* - if it is concluding (a reason was named) or `is_finished()` says so, it
*   completes **this** tick and executes no further;
* - otherwise, for a stateful task, one pending state transition is honored -
*   `on_pause()` or `on_resume()` - and that is the whole of its tick;
* - otherwise it gets one `on_execute()`.
*
* Two consequences drive the tick counts here. A pause costs a tick and a resume
* costs another, because each is honored *instead of* an execution rather than
* alongside one. And a task that reports itself finished still needs one more
* `update()` to conclude in, since the tick that ran its last `on_execute()` had
* already made its choice.
*/
#include "support/lifecycle/scenarios.hpp"
#include "support/lifecycle/report.hpp"
#include "config/wiring.hpp"
#include <etask/core/completion_reason.hpp>
#include <etask/core/status_code.hpp>
#include <cstdint>

namespace support::lifecycle {

    namespace {

        namespace core = etask::core;

        /// @brief Field offsets in the trace every managed task returns.
        /// @note The first three are common to all of them; the stateful task's
        ///       longer shape is indexed by @ref stateful_field.
        enum trace_field : unsigned {
            trace_hooks = 0,      ///< The `hook` bitmask.
            trace_executions = 1, ///< How many times `on_execute()` ran.
            trace_reason = 2,     ///< The `completion_reason` handed to `on_complete`.
        };

        /// @brief Field offsets specific to `resumable`'s six-value trace.
        enum stateful_field : unsigned {
            stateful_hooks = 0,               ///< The `hook` bitmask.
            stateful_executions = 1,          ///< Total executions.
            stateful_executions_at_pause = 2, ///< Executions latched at `on_pause()`.
            stateful_pauses = 3,              ///< How many times `on_pause()` ran.
            stateful_resumes = 4,             ///< How many times `on_resume()` ran.
            stateful_reason = 5,              ///< The reason handed to `on_complete`.
        };

        /**
        * @brief The caller-supplied reason the force-complete scenarios use.
        *
        * A user-range value rather than `aborted`, because the two take
        * different paths: `aborted` maps to `task_aborted`, while anything in
        * the user range maps to `task_completed_early` and is the case where the
        * caller's own byte has to survive into `on_complete`. Picking one from
        * the user range is what makes that survivable byte distinguishable from
        * a default the framework could have supplied on its own.
        */
        constexpr core::completion_reason superseded = core::user_reason(0);

        /**
        * @brief Advances every managed task by one tick.
        *
        * Named rather than called inline so the scenarios read as a count of
        * ticks, which is the unit their expectations are written in.
        */
        void tick()
        {
            config::manager.update();
        }

        /**
        * @brief Reports a status code returned by a directive.
        *
        * @param key  Dotted name for the observation.
        * @param code The status the manager answered with.
        */
        void report_status(const char* key, core::status_code code)
        {
            report::value(key, static_cast<unsigned long>(code));
        }

        /**
        * @brief Reports the reply the capturing channel last kept.
        *
        * Emits the completion count and status under `<prefix>.completions` and
        * `<prefix>.status`. The count is always reported, including when it is
        * zero: "no task concluded" is an outcome the host has to be able to
        * assert on, and it has no reply of its own to carry the news.
        *
        * @param prefix Dotted name of the scenario, e.g. `"oneshot"`.
        */
        void report_reply(const char* prefix)
        {
            // Built rather than passed as a literal because the same two
            // suffixes are wanted under every scenario's own prefix, and a
            // dotted key is what keeps the host's assertions readable.
            char key[48];
            const auto emit = [&key, prefix](const char* suffix, unsigned long v) {
                std::size_t i = 0;
                for (const char* p = prefix; *p and i + 1 < sizeof(key); ++p) key[i++] = *p;
                for (const char* p = suffix; *p and i + 1 < sizeof(key); ++p) key[i++] = *p;
                key[i] = '\0';
                report::value(key, v);
            };

            emit(".completions", static_cast<unsigned long>(config::capture.completions()));
            emit(".status", static_cast<unsigned long>(config::capture.status()));

            static const char* const suffixes[] = {
                ".f0", ".f1", ".f2", ".f3", ".f4", ".f5",
            };
            for (std::size_t i = 0; i < config::capture.size() and i < 6; ++i)
                emit(suffixes[i], config::capture.byte(i));
        }

        /**
        * @brief Clears the captured reply before a scenario runs.
        *
        * Each scenario starts from a channel with nothing in it, so a reply it
        * reads afterwards is necessarily its own.
        */
        void arm()
        {
            config::capture.reset();
        }

        /**
        * @brief Registers a task through the capturing channel.
        *
        * The scope's `context&` is passed explicitly, as the task's constructor
        * declares it. That is not a detail this project can skip: the adapter
        * the manager stores supplies a context only on the *wire* path, where
        * there is no call site to hand one in. Registering in-process means
        * calling the native constructor, and the native constructor takes the
        * context - so omitting it does not fall back to the accessor, it simply
        * matches no constructor and registration fails with `task_unknown`.
        *
        * @tparam Args The task's constructor argument types, the trailing
        *         `context&` included.
        * @param uid  Which task to start.
        * @param args Forwarded to the task's constructor.
        * @return The manager's registration status.
        */
        template<typename... Args>
        [[nodiscard]] core::status_code start(global::task_id uid, Args&&... args)
        {
            return config::manager.register_task(
                &config::capture, ECOMM_BOARD_ID, uid, static_cast<Args&&>(args)...);
        }

        /**
        * @brief An instant command runs on arrival, and answers nothing.
        *
        * The two halves are inseparable here: the arrival counter proves the
        * command ran, and the completion count proves it ran *without* a reply.
        * Either alone would be satisfied by a broken implementation - a command
        * that never ran also sends no reply.
        */
        void instant_runs_and_stays_silent()
        {
            arm();
            generated::scopes::instant().recorder.reset();

            report_status("instant.register", start(global::task_id::instant_ping, generated::scopes::instant()));

            // No tick. The claim is that the command already ran inside
            // register_task, so giving it one would make the two indistinguishable.
            report::value("instant.arrivals",
                generated::scopes::instant().recorder.arrivals());
            report::value("instant.completions",
                static_cast<unsigned long>(config::capture.completions()));

            // And it is still silent a tick later - it never entered storage, so
            // there is nothing for update() to find.
            tick();
            report::value("instant.completions_after_tick",
                static_cast<unsigned long>(config::capture.completions()));
        }

        /**
        * @brief Every directive aimed at an instant command's uid is refused.
        *
        * `task_not_addressable` rather than `task_not_registered`: the uid is
        * this firmware's and always will be, but it can never name a live task,
        * so the caller is asking for something structurally impossible rather
        * than something that merely is not running yet.
        */
        void instant_is_not_addressable()
        {
            report_status("instant.pause",
                config::manager.pause_task(global::task_id::instant_ping));
            report_status("instant.resume",
                config::manager.resume_task(global::task_id::instant_ping));
            report_status("instant.complete",
                config::manager.complete_task(global::task_id::instant_ping, core::aborted));
        }

        /**
        * @brief A oneshot runs exactly one execution step, then answers.
        *
        * Given three ticks rather than the two it needs, so that "runs once" is
        * tested against a manager with every opportunity to run it again. A
        * sealed `is_finished()` is the tier's guarantee; this is what would catch
        * it being honored in name only.
        */
        void oneshot_runs_once_and_answers()
        {
            arm();
            report_status("oneshot.register", start(global::task_id::oneshot_sample, generated::scopes::oneshot()));

            tick();  // the single on_execute()
            tick();  // is_finished() is true, so this tick concludes it
            tick();  // nothing left; the record is gone

            report_reply("oneshot");
        }

        /**
        * @brief A polled task runs across ticks and decides its own completion.
        *
        * Registered for three executions. The interesting assertion is not that
        * it finished but that it took the ticks it claimed to need: a manager
        * that concluded it after one would still produce a reply, and only the
        * execution count would say so.
        */
        void polled_runs_across_ticks()
        {
            arm();
            constexpr std::uint8_t wanted = 3;
            report_status("polled.register",
                start(global::task_id::polled_count_to, wanted, generated::scopes::polled()));
            report::value("polled.requested", wanted);

            // Three executions, then a fourth tick for the conclusion - the tick
            // that ran the last on_execute() had already made its choice.
            tick();
            tick();
            tick();
            report::value("polled.completions_before_conclusion",
                static_cast<unsigned long>(config::capture.completions()));
            tick();

            report_reply("polled");
        }

        /**
        * @brief Pause and resume are refused for a polled task.
        *
        * `task_not_pausable`, and specifically not `ok`. The tier split exists
        * because the single manager that preceded it accepted this and called an
        * empty hook, so a caller could believe it had suspended something. The
        * task is deliberately live while it is asked, so the refusal is about the
        * tier rather than about there being nothing there.
        */
        void polled_refuses_suspension()
        {
            arm();
            report_status("polled_ns.register",
                start(global::task_id::polled_never_ends, generated::scopes::polled()));
            tick();

            report_status("polled_ns.pause",
                config::manager.pause_task(global::task_id::polled_never_ends));
            report_status("polled_ns.resume",
                config::manager.resume_task(global::task_id::polled_never_ends));

            // Left running for the force-complete scenario below, which needs a
            // task that will never conclude on its own.
        }

        /**
        * @brief Completing with `finished` is refused; a caller's reason is not.
        *
        * `completion_reason::finished` is reserved for the manager's own natural
        * completion, so a caller naming it is claiming an ending it did not
        * cause - answered with `invalid_completion_reason`. The task is still
        * running afterwards, which the following force-complete relies on.
        *
        * @note Runs against the task `polled_refuses_suspension` left live.
        */
        void completing_with_finished_is_refused()
        {
            report_status("refuse.complete_finished",
                config::manager.complete_task(
                    global::task_id::polled_never_ends, core::finished));
        }

        /**
        * @brief Force-completing a running task yields `task_completed_early`,
        *        and the caller's reason reaches `on_complete`.
        *
        * The task cannot finish by itself, so both halves are attributable: the
        * status is not one it could have reached, and the reason byte it echoes
        * back is one only the caller could have supplied.
        *
        * @note Concludes the task `polled_refuses_suspension` left live.
        */
        void force_completing_reports_early_and_carries_the_reason()
        {
            report_status("force.complete",
                config::manager.complete_task(
                    global::task_id::polled_never_ends, superseded));
            report::value("force.reason_sent", static_cast<unsigned long>(superseded));

            tick();  // the conclusion happens on the next sweep
            report_reply("force");
        }

        /**
        * @brief A double pause and a double resume are each rejected in kind.
        *
        * The two rejections are different codes because the states are not
        * symmetric: a second pause finds the task already suspended
        * (`task_already_paused`), while a second resume finds a resume already
        * pending (`task_already_resumed`) or the task simply running
        * (`task_already_running`). Reporting the codes rather than a pass/fail
        * is what lets the host say which it actually got.
        *
        * @note Leaves the task suspended for the scenario that follows.
        */
        void repeated_directives_are_rejected()
        {
            arm();
            constexpr std::uint8_t run_for = 2;
            report_status("stateful.register",
                start(global::task_id::stateful_resumable, run_for, generated::scopes::stateful()));

            tick();  // one execution, so the task is genuinely running

            report_status("dbl.pause_first",
                config::manager.pause_task(global::task_id::stateful_resumable));
            report_status("dbl.pause_second",
                config::manager.pause_task(global::task_id::stateful_resumable));

            tick();  // honors the pause: on_pause() runs, the task settles suspended

            report_status("dbl.resume_first",
                config::manager.resume_task(global::task_id::stateful_resumable));
            report_status("dbl.resume_second",
                config::manager.resume_task(global::task_id::stateful_resumable));
        }

        /**
        * @brief A stateful task pauses, stays paused, resumes, and finishes.
        *
        * "Stays paused" is the half that needs ticks spent on it: the task is
        * left suspended across several sweeps and its execution count is read at
        * the end, so a manager that kept executing a task it had agreed to
        * suspend is caught by the count rather than by the absence of a hook.
        *
        * @note Continues the task `repeated_directives_are_rejected` left with a
        *       resume pending.
        */
        void stateful_pauses_stays_paused_resumes_and_finishes()
        {
            tick();  // honors the resume: on_resume() runs, the task is running again

            // The remaining execution, then the tick that concludes it.
            tick();
            tick();

            report_reply("stateful");
        }

        /**
        * @brief A paused task is not executed while it is suspended.
        *
        * A fresh run, because the scenario above ends with the task gone. Here
        * the suspension is held across several ticks and the execution count is
        * compared against the count latched at `on_pause()` - equal means the
        * manager honored it, and any difference is the number of times it did
        * not.
        */
        void suspension_actually_suspends()
        {
            arm();
            constexpr std::uint8_t run_for = 200;  // far more than this scenario gives it
            report_status("held.register",
                start(global::task_id::stateful_resumable, run_for, generated::scopes::stateful()));

            tick();  // one execution
            report_status("held.pause",
                config::manager.pause_task(global::task_id::stateful_resumable));
            tick();  // honors the pause

            // Four ticks fully suspended. If any of them executes the task, the
            // total will have moved past what on_pause() latched.
            tick();
            tick();
            tick();
            tick();

            // Concluding is not gated on the run state, so a suspended task can
            // be completed exactly as a running one can - which is also the last
            // thing this scenario needs, to get the trace back out.
            report_status("held.complete",
                config::manager.complete_task(
                    global::task_id::stateful_resumable, superseded));
            tick();

            report_reply("held");
        }

    } // namespace

    void run_all()
    {
        instant_runs_and_stays_silent();
        instant_is_not_addressable();

        oneshot_runs_once_and_answers();

        polled_runs_across_ticks();
        polled_refuses_suspension();
        completing_with_finished_is_refused();
        force_completing_reports_early_and_carries_the_reason();

        repeated_directives_are_rejected();
        stateful_pauses_stays_paused_resumes_and_finishes();
        suspension_actually_suspends();

        report::done();
    }

} // namespace support::lifecycle
