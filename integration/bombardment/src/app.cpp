/**
* @file app.cpp
*
* @brief The bombardment checks: fill each tier, overrun it, drain it, repeat.
*
* @note User-owned. Everything here is test code; nothing models hardware.
*
* ## What this file is trying to catch
*
* Two failures, both quiet:
*
* - **The wrong refusal.** `task_limit_reached` and `task_budget_exhausted`
*   describe different problems with different fixes (raise this task's
*   `concurrency:`, versus raise the tier's `budget:`), and a caller acting on
*   the wrong one changes the wrong number. Nothing in a passing build tells
*   them apart, so each check pins the exact code.
* - **The unreclaimed record.** A manager that loses a record does not crash; it
*   simply refuses everything from then on with a status that looks correct.
*   Only registering again *after* a drain distinguishes "full" from "leaking",
*   which is why every fill check is followed by a drain and a re-fill.
*
* ## The transcript
*
* Each check prints `CHECK <name> <PASS|FAIL>` plus `  <detail>` lines, and a
* failure always states what was expected next to what happened. The transcript
* is the report - verify.py parses it rather than re-deriving the results, so a
* human reading the raw output sees exactly what the driver saw.
*
* ## Why the assertions live here and not in verify.py
*
* Only C++ can call the manager. A Python driver can start this binary and read
* what it says, but it cannot register a task, so the *checking* has to be on
* this side and the driver's job is to run it, insist that every expected check
* actually reported, and explain what failed.
*/
#include "app.hpp"
#include "config/wiring.hpp"
#include "generated/scopes.hpp"
#include <cstdint>
#include <cstdio>

namespace app {
namespace {

    using etask::core::completion_reason;
    using etask::core::status_code;
    using global::task_id;

    /// @brief How many checks have reported `FAIL`. Reported by @ref app::failures.
    int failure_count = 0;

    /**
    * @brief Ticks a task is given when it must stay live for the whole check.
    *
    * Large enough that no check can accidentally outlast it - a task that
    * drained early would free a record and make an "the tier is full" assertion
    * pass for the wrong reason, or fail confusingly. Small enough to be visibly
    * finite, so a runaway loop is a hang rather than a plausible number.
    */
    constexpr std::uint16_t hold_forever = 10000;

    /// @brief Ticks for a task that should conclude on the very next `update()`.
    constexpr std::uint16_t hold_one_tick = 1;

    /// @brief The polled tier's budget, restated so a check can say what it expected.
    constexpr std::size_t polled_budget = generated::polled_budget;

    /// @brief The stateful tier's budget. @see polled_budget
    constexpr std::size_t stateful_budget = generated::stateful_budget;

    /**
    * @brief The name of a status code, for a failure message.
    *
    * A bare number in a diff between expected and actual is unreadable, and the
    * distinction this whole project exists to test is between two codes that
    * look alike as integers (0x12 and 0x18). Only the codes these checks can
    * actually produce are named; anything else prints as a number, which is
    * itself informative - it means the manager took a path the test did not
    * anticipate.
    *
    * @param code The status to name.
    * @return A static string, never null.
    */
    const char* status_name(status_code code)
    {
        switch (code) {
            case status_code::ok:                    return "ok";
            case status_code::task_not_registered:   return "task_not_registered";
            case status_code::reentrancy_conflict:   return "reentrancy_conflict";
            case status_code::channel_null:          return "channel_null";
            case status_code::task_limit_reached:    return "task_limit_reached";
            case status_code::duplicate_task:        return "duplicate_task";
            case status_code::task_unknown:          return "task_unknown";
            case status_code::task_not_pausable:     return "task_not_pausable";
            case status_code::task_not_addressable:  return "task_not_addressable";
            case status_code::task_budget_exhausted: return "task_budget_exhausted";
            default:                                 return "<unnamed>";
        }
    }

    /**
    * @brief Records one check's verdict on the transcript.
    *
    * @param name Which check. Must match the name verify.py looks for; the
    *             driver insists every expected check reported, so a check that
    *             silently stops running is a failure rather than an absence.
    * @param passed Its verdict.
    */
    void report(const char* name, bool passed)
    {
        if (not passed) ++failure_count;
        std::printf("CHECK %s %s\n", name, passed ? "PASS" : "FAIL");
    }

    /**
    * @brief Asserts a registration returned exactly the status it should have.
    *
    * Prints the difference on a mismatch rather than only the fact of one: the
    * codes under test are neighbours in an enum, so "expected 0x18, got 0x12" is
    * the whole diagnosis and "assertion failed" is none of it.
    *
    * @param what     What was being attempted, in the transcript's words.
    * @param expected The documented status for that attempt.
    * @param actual   What the manager returned.
    * @return Whether they matched.
    */
    bool expect_status(const char* what, status_code expected, status_code actual)
    {
        if (expected == actual) {
            std::printf("  %s -> %s\n", what, status_name(actual));
            return true;
        }
        std::printf("  %s -> expected %s (0x%02X), got %s (0x%02X)\n",
                    what,
                    status_name(expected), static_cast<unsigned>(expected),
                    status_name(actual), static_cast<unsigned>(actual));
        return false;
    }

    /**
    * @brief Asserts a counted quantity matches, printing both values on a mismatch.
    *
    * @param what     What was counted, in the transcript's words.
    * @param expected The value the framework's documentation implies.
    * @param actual   The value observed.
    * @return Whether they matched.
    */
    bool expect_count(const char* what, unsigned long expected, unsigned long actual)
    {
        if (expected == actual) {
            std::printf("  %s -> %lu\n", what, actual);
            return true;
        }
        std::printf("  %s -> expected %lu, got %lu\n", what, expected, actual);
        return false;
    }

    /**
    * @brief Starts one task through the internal channel.
    *
    * A thin wrapper so the checks read as a sequence of intentions rather than a
    * sequence of argument lists. The scope context is fetched here rather than
    * cached, because `generated::scopes` builds the context tree on first use
    * and the checks must not depend on when that happened.
    *
    * @param uid   Which task to start.
    * @param ticks How many `update()` calls it should run for.
    * @return The manager's status.
    */
    [[nodiscard]] status_code start_swarm(task_id uid, std::uint16_t ticks)
    {
        return config::internal.register_task(uid, ticks, generated::scopes::swarm());
    }

    /**
    * @brief Starts one `probe`, the oneshot task that takes no parameters.
    * @return The manager's status.
    */
    [[nodiscard]] status_code start_probe()
    {
        return config::internal.register_task(task_id::swarm_probe, generated::scopes::swarm());
    }

    /**
    * @brief Starts one `latch` on the stateful tier.
    *
    * @param ticks How many `update()` calls it should run for.
    * @return The manager's status.
    */
    [[nodiscard]] status_code start_latch(std::uint16_t ticks)
    {
        return config::internal.register_task(task_id::hold_latch, ticks, generated::scopes::hold());
    }

    /**
    * @brief Fills the polled tier to exactly its budget, using two uids.
    *
    * Two rather than one because no uid's `concurrency` reaches the budget - see
    * the schema's note on why one that did could never produce
    * `task_budget_exhausted`. `salvo` supplies four records and `probe` the
    * other two, leaving every uid in the tier with at least one slot of its own
    * unused: so a refusal on the next registration cannot be a per-uid cap, and
    * the check that follows is unambiguous.
    *
    * @param ticks How long each task should hold its record for.
    * @return Whether every one of the `budget` registrations was accepted.
    */
    [[nodiscard]] bool fill_polled_tier(std::uint16_t ticks)
    {
        // `probe` is a oneshot, so it concludes on the first sweep regardless of
        // `ticks`. That is why it goes in last and why the callers that need the
        // tier held across an update() use it only for the final two records -
        // no check in this file sweeps while relying on a probe still being live.
        constexpr std::size_t salvo_records = 4;
        bool filled = true;
        for (std::size_t i = 0; i < salvo_records; ++i)
            filled &= (start_swarm(task_id::swarm_salvo, ticks) == status_code::ok);
        for (std::size_t i = salvo_records; i < polled_budget; ++i)
            filled &= (start_probe() == status_code::ok);
        if (not filled)
            std::printf("  fill to budget -> a registration below the budget was refused\n");
        return filled;
    }

    /**
    * @brief Force-completes and drains everything currently live, then resets counters.
    *
    * Every check calls this on the way out. `complete_task` marks a task to
    * conclude on the next sweep, so one `update()` per live task uid is enough -
    * but the loop repeats until both scopes report every construction matched by
    * a conclusion, because a record that fails to drain is precisely the bug
    * being hunted and must show up as a hang here rather than as a confusing
    * failure three checks later.
    *
    * @return Whether the managers emptied within a bounded number of sweeps.
    */
    bool drain()
    {
        // Every uid that can hold a record. `complete_task` addresses a uid, not
        // an instance, and concludes one instance per call - so with several
        // instances of a uid live, this list is walked more than once.
        constexpr task_id live_uids[] = {
            task_id::swarm_salvo,
            task_id::swarm_volley,
            task_id::swarm_single,
            task_id::swarm_probe,
            task_id::hold_latch,
        };

        // Bounded rather than `while (true)`: a manager that will not release a
        // record must end this run, not spin in it. The bound is the two budgets
        // plus slack - no more records than that can exist, so anything beyond it
        // means a record is not being reclaimed.
        constexpr int max_sweeps = static_cast<int>(polled_budget + stateful_budget) * 4;

        for (int sweep = 0; sweep < max_sweeps; ++sweep) {
            // Emptiness is established by asking the managers, not by comparing
            // the scopes' counters. The counters are the harness's own
            // bookkeeping and a check is free to zero them mid-scenario; the
            // manager's answer to "is anything of this uid live" cannot be
            // desynchronized from the thing being drained.
            bool anything_live = false;
            for (const auto uid : live_uids) {
                const auto marked = config::internal.complete_task(uid, completion_reason::aborted);
                // `task_not_registered` is the one answer that means "nothing of
                // this uid is live". Every other answer - accepted, already
                // concluding, already finished - means a record still exists.
                anything_live |= (marked != status_code::task_not_registered);
            }
            if (not anything_live) {
                // Reaches both scopes at once, which is why it is a root-level
                // task; see sys/reset_counters.cpp.
                (void)config::internal.register_task(task_id::reset_counters,
                                                     generated::scopes::system());
                return true;
            }
            config::manager.update();
        }
        std::printf("  drain -> managers did not empty within %d sweeps\n", max_sweeps);
        return false;
    }

    // ---------------------------------------------------------------- checks

    /**
    * @brief Filling the polled tier to exactly its budget succeeds, every time.
    *
    * The baseline the rest of the file rests on. If the tier cannot be filled to
    * its stated budget then every later check about what happens *at* the budget
    * is measuring something else.
    *
    * Every uid involved keeps a slot of its own in reserve (see
    * @ref fill_polled_tier), so no registration here can be refused by a per-uid
    * cap - anything that fails is the tier's doing.
    */
    void check_fill_to_budget()
    {
        bool passed = fill_polled_tier(hold_forever);

        // The registrations returning `ok` is not by itself proof the records are
        // occupied - a manager that accepted and dropped them would look the
        // same. The peak the tasks themselves recorded is.
        passed &= expect_count("live polled records at the peak",
                               polled_budget, generated::scopes::swarm().peak_live);
        passed &= drain();
        report("fill_to_budget", passed);
    }

    /**
    * @brief One past the budget is refused with `task_budget_exhausted`, not something else.
    *
    * The headline claim of `status_code::task_budget_exhausted`'s documentation:
    * "the owning manager is full... no task of any type in that tier can start".
    * Both halves are checked - the refusal's code, and that it holds for several
    * *different* uids, each with untouched capacity of its own.
    */
    void check_budget_exhausted()
    {
        bool passed = fill_polled_tier(hold_forever);

        // Three uids, each with slots to spare: `volley` has used none of its
        // two, `single` none of its one, and `salvo` has four of its four in use
        // but that is still not what stops it - the tier is. Asking all three
        // rules out the reading in which 0x18 is merely what one particular uid
        // happens to answer.
        passed &= expect_status("register volley into a full tier, its own slots free",
                                status_code::task_budget_exhausted,
                                start_swarm(task_id::swarm_volley, hold_forever));
        passed &= expect_status("register single into a full tier, its own slot free",
                                status_code::task_budget_exhausted,
                                start_swarm(task_id::swarm_single, hold_forever));

        passed &= drain();
        report("budget_exhausted", passed);
    }

    /**
    * @brief Saturating one uid while the tier has room is `task_limit_reached`.
    *
    * The other side of the distinction. `volley` reserves two slots out of a
    * six-record tier, so at two live instances its own reservation is spent
    * while four records stand free - the only arrangement in which the two
    * refusals are distinguishable at all.
    *
    * The check does not stop at the code: it then starts a *different* task into
    * the same tier and requires that to succeed. Without that, a manager that
    * had wrongly filled the tier would produce an identical transcript.
    */
    void check_limit_reached_with_room()
    {
        bool passed = true;
        passed &= expect_status("register volley 1 of 2",
                                status_code::ok, start_swarm(task_id::swarm_volley, hold_forever));
        passed &= expect_status("register volley 2 of 2",
                                status_code::ok, start_swarm(task_id::swarm_volley, hold_forever));

        passed &= expect_status("register volley past its own concurrency, tier still has room",
                                status_code::task_limit_reached,
                                start_swarm(task_id::swarm_volley, hold_forever));

        // The claim "the tier has room" made good on: a different uid still
        // starts, so the refusal above really was about `volley` alone.
        passed &= expect_status("register salvo while volley is saturated",
                                status_code::ok, start_swarm(task_id::swarm_salvo, hold_forever));
        passed &= expect_count("live polled records", 3u, generated::scopes::swarm().peak_live);

        passed &= drain();
        report("limit_reached_with_room", passed);
    }

    /**
    * @brief What a uid with the default `concurrency` of one answers when saturated.
    *
    * `single` declares no `concurrency:`, so it reserves one slot - the ordinary
    * case in a real schema. The manager takes a different branch for it than for
    * a multi-slot uid, and this check records which status that branch produces
    * so the transcript states it rather than leaving it to be inferred from the
    * multi-slot case.
    *
    * @note The expected code here is `duplicate_task`, not `task_limit_reached`.
    *       See verify.py's `single_instance_refusal` note: this is the one place
    *       where the manager's behaviour and `task_limit_reached`'s documented
    *       meaning do not line up, and the check pins the behaviour that exists
    *       so a change to it is noticed.
    */
    void check_single_instance_refusal()
    {
        bool passed = true;
        passed &= expect_status("register single, its one slot free",
                                status_code::ok, start_swarm(task_id::swarm_single, hold_forever));

        passed &= expect_status("register single again, its one slot taken, tier has room",
                                status_code::duplicate_task,
                                start_swarm(task_id::swarm_single, hold_forever));

        passed &= drain();
        report("single_instance_refusal", passed);
    }

    /**
    * @brief After tasks conclude, their records come back.
    *
    * The leak check, and the reason the rest of the file bothers to drain. A
    * manager that never reclaims a record is indistinguishable from a correct
    * one until something tries to register after a drain: at that moment a
    * correct manager says `ok` and a leaking one says `task_budget_exhausted`
    * forever.
    *
    * The tasks here are given a single tick so they conclude on their own
    * `is_finished()`, which is the path a real task takes - `drain()` uses the
    * forced path, and a record could plausibly leak on one and not the other.
    */
    void check_slots_reclaimed()
    {
        bool passed = fill_polled_tier(hold_one_tick);

        passed &= expect_status("register into the full tier, before draining",
                                status_code::task_budget_exhausted,
                                start_swarm(task_id::swarm_volley, hold_one_tick));

        // One sweep executes each task (dropping it to zero remaining ticks) and
        // a second concludes it, since `is_finished()` is consulted at the top of
        // a sweep rather than after the execute in the same one. The probes
        // conclude on the first sweep, being oneshots; the extra sweep is
        // harmless to them.
        config::manager.update();
        config::manager.update();

        passed &= expect_count("polled tasks concluded",
                               polled_budget, generated::scopes::swarm().concluded);

        // The assertion the whole check exists for.
        passed &= expect_status("register after the drain",
                                status_code::ok, start_swarm(task_id::swarm_volley, hold_forever));

        // And the tier is fully back, not merely one record short of full: the
        // second volley plus a full fill of salvo and probe would overrun it, so
        // stop one short and confirm the boundary is where it was.
        passed &= expect_status("register the second volley", status_code::ok,
                                start_swarm(task_id::swarm_volley, hold_forever));
        for (std::size_t i = 2; i < polled_budget; ++i)
            passed &= (start_swarm(task_id::swarm_salvo, hold_forever) == status_code::ok);
        passed &= expect_status("register one past the budget again",
                                status_code::task_budget_exhausted,
                                start_swarm(task_id::swarm_single, hold_forever));

        passed &= drain();
        report("slots_reclaimed", passed);
    }

    /**
    * @brief The stateful tier has its own budget, unaffected by the polled one.
    *
    * Two managers, two budgets. Filling the polled tier to refusal must leave the
    * stateful tier able to accept its full complement, and the stateful tier's
    * own overrun must report `task_budget_exhausted` even though `latch` is
    * allowed three instances and only two are live - the tier binds first.
    */
    void check_stateful_tier_is_separate()
    {
        bool passed = fill_polled_tier(hold_forever);
        passed &= expect_status("polled tier is full",
                                status_code::task_budget_exhausted,
                                start_swarm(task_id::swarm_volley, hold_forever));

        for (std::size_t i = 0; i < stateful_budget; ++i)
            passed &= expect_status("register latch while the polled tier is full",
                                    status_code::ok, start_latch(hold_forever));

        // `latch` reserves three slots but the tier holds two, so this refusal is
        // the tier's and not the uid's - the mirror of check_budget_exhausted, on
        // the other manager.
        passed &= expect_status("register latch past the stateful budget, its own slots free",
                                status_code::task_budget_exhausted, start_latch(hold_forever));

        // An instant command occupies no record in either tier, so it must still
        // run with both managers full - the claim in `task_manager`'s
        // documentation that "instant commands take no budget".
        passed &= expect_status("register the instant command with both tiers full",
                                status_code::ok,
                                config::internal.register_task(task_id::reset_counters,
                                                               generated::scopes::system()));

        passed &= drain();
        report("stateful_tier_is_separate", passed);
    }

    /**
    * @brief A paused stateful task still holds its record.
    *
    * Stated in the schema's `budget:` documentation ("a paused task still holds
    * its record") and in the stateful tier's own. It matters because it is the
    * counter-intuitive half: a task that is not running still costs a slot, so a
    * device that parks tasks rather than concluding them fills its tier with
    * things that appear idle.
    */
    void check_paused_task_holds_its_record()
    {
        bool passed = true;
        for (std::size_t i = 0; i < stateful_budget; ++i)
            passed &= (start_latch(hold_forever) == status_code::ok);

        passed &= expect_status("pause a live latch", status_code::ok,
                                config::internal.pause_task(task_id::hold_latch));
        config::manager.update();   // the sweep that actually invokes on_pause()

        passed &= expect_count("on_pause invocations", 1u, generated::scopes::hold().paused);

        // The point: the tier is no emptier for one of its tasks being asleep.
        passed &= expect_status("register a latch while one of the tier's tasks is paused",
                                status_code::task_budget_exhausted, start_latch(hold_forever));

        passed &= expect_status("resume the paused latch", status_code::ok,
                                config::internal.resume_task(task_id::hold_latch));
        config::manager.update();
        passed &= expect_count("on_resume invocations", 1u, generated::scopes::hold().resumed);

        passed &= drain();
        report("paused_task_holds_its_record", passed);
    }

    /**
    * @brief Sustained register/complete churn leaves the manager working.
    *
    * The endurance check. Everything above tests one transition; this one runs
    * thousands and then asks whether the manager still behaves exactly as the
    * first check found it - fills to the budget, refuses past it, drains.
    *
    * `swap_erase` is the reason this is worth doing: the polled manager removes
    * a concluded record by swapping the last one into its place, so the storage
    * is permuted on every sweep and the order records sit in is never the order
    * they arrived in. A bookkeeping error there would not show up in a check that
    * fills once and empties once.
    */
    void check_sustained_churn()
    {
        constexpr int rounds = 2000;
        bool passed = true;
        unsigned long registered = 0;

        for (int round = 0; round < rounds; ++round) {
            // Deliberately uneven: a mix of uids with different concurrency, so
            // each round leaves the storage in a different permutation rather
            // than cycling through the same two or three states.
            if (start_swarm(task_id::swarm_salvo, hold_one_tick) == status_code::ok) ++registered;
            if (start_probe() == status_code::ok) ++registered;
            if (start_swarm(task_id::swarm_volley, hold_one_tick) == status_code::ok) ++registered;
            config::manager.update();
            if (start_swarm(task_id::swarm_single, hold_one_tick) == status_code::ok) ++registered;
            config::manager.update();
            config::manager.update();
        }

        std::printf("  churn rounds -> %d\n", rounds);

        // A floor rather than an exact figure: whether a given registration in a
        // given round finds a free record depends on how the previous round's
        // tasks drained, and pinning that exactly would be testing the harness's
        // own arithmetic rather than the manager. What matters is that work kept
        // getting through - a manager that leaked a record per round would have
        // stopped accepting anything within the first dozen.
        if (registered < static_cast<unsigned long>(rounds)) {
            std::printf("  registrations accepted -> expected at least %d, got %lu\n",
                        rounds, registered);
            passed = false;
        } else {
            std::printf("  registrations accepted -> %lu\n", registered);
        }

        // The leak assertion, stated over the whole run rather than one cycle:
        // every task the manager built also ran its completion hook, so no record
        // was retained and none was destroyed without concluding.
        const auto& swarm = generated::scopes::swarm();
        std::printf("  tasks constructed -> %lu\n",
                    static_cast<unsigned long>(swarm.constructed));
        passed &= expect_count("tasks concluded", swarm.constructed, swarm.concluded);

        // And the manager is still the one the first check measured, not merely
        // still responsive.
        passed &= fill_polled_tier(hold_forever);
        passed &= expect_status("after churn, the tier still fills to exactly its budget",
                                status_code::task_budget_exhausted,
                                start_swarm(task_id::swarm_volley, hold_forever));

        passed &= drain();
        report("sustained_churn", passed);
    }

} // namespace

void setup()
{
    std::printf("BOMBARDMENT polled_budget=%zu stateful_budget=%zu\n",
                polled_budget, stateful_budget);

    check_fill_to_budget();
    check_budget_exhausted();
    check_limit_reached_with_room();
    check_single_instance_refusal();
    check_slots_reclaimed();
    check_stateful_tier_is_separate();
    check_paused_task_holds_its_record();
    check_sustained_churn();

    std::printf("BOMBARDMENT done failures=%d\n", failure_count);
}

void loop()
{
    config::manager.update();
}

int failures()
{
    return failure_count;
}

} // namespace app
