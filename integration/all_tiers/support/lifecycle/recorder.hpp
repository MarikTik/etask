/**
* @file recorder.hpp
*
* @brief The instrument this project measures with: a per-scope ledger of which
*        lifecycle hooks ran, in what order, and how often.
*
* @note User-owned. The generator never writes here.
*
* ## Why a recorder rather than assertions in the hooks
*
* A hook that asserts can only fail the run; it cannot say what the manager did
* instead. This project's whole subject is *sequence* - `on_pause()` before the
* suspended stretch, `on_resume()` after it, `on_complete()` exactly once at the
* end - so a hook has to leave evidence that outlives it and can be compared
* against an expectation after the fact.
*
* Evidence is kept in two forms, because they fail differently:
*
* - a **bitmask** of which hooks ran at all. A hook that never fires is the
*   quietest possible failure: nothing happens, the task still concludes, and
*   the status code is the one the caller hoped for. The mask is what turns that
*   into a visible zero bit.
* - **counters** for how many times each ran. `on_execute()` firing once when
*   three ticks were given, or twice when a suspension should have blocked it,
*   is a different fault from it never firing - and only a count separates them.
*
* A task that concludes hands both back through its `outcome`, which is why the
* schema's `returns:` shapes are trace-shaped rather than result-shaped.
*
* ## Why the counters saturate
*
* Every field is a `std::uint8_t`, because that is what the schema declares and
* what crosses the wire. A runaway task - the failure mode `never_ends` exists
* to provoke - would wrap a raw counter back through zero and could land on the
* expected value, reporting success for a task that ran 256 times too many.
* Saturating at 255 makes an overrun stay wrong.
*/
#ifndef SUPPORT_LIFECYCLE_RECORDER_HPP_
#define SUPPORT_LIFECYCLE_RECORDER_HPP_
#include <cstdint>

namespace support::lifecycle {

    /**
    * @enum hook
    *
    * @brief One bit per lifecycle hook, as reported in a trace's `hooks` field.
    *
    * The values are a wire contract with `verify.py`, which reconstructs the
    * sequence from them - so they are written explicitly rather than shifted
    * from an ordinal, and their order here is the order a task runs them in.
    *
    * `construct` earns a bit despite not being a hook the manager calls: for an
    * @ref instant_task the constructor *is* the entire task, so without it that
    * tier would have no evidence of running at all.
    */
    enum hook : std::uint8_t {
        construct = 0x01, ///< The task was built. For an instant command, the whole of it.
        execute   = 0x02, ///< `on_execute()` ran at least once.
        pause     = 0x04, ///< `on_pause()` ran - only ever legal on a stateful task.
        resume    = 0x08, ///< `on_resume()` ran.
        finish    = 0x10, ///< `is_finished()` was polled at least once.
        complete  = 0x20, ///< `on_complete()` ran. Exactly once, on every path.
    };

    /**
    * @class recorder
    *
    * @brief The ledger a scope's tasks write their lifecycle into.
    *
    * One lives in each scope's `context`, so the tasks of a tier share exactly
    * one and no other tier can write to it. That isolation is what lets a trace
    * be read as belonging to the tier it came from.
    *
    * Not thread-safe, and deliberately so: the task lifecycle is cooperative and
    * single-threaded by construction - every hook runs inside `update()` on the
    * one loop - so a lock here would guard against a caller the framework does
    * not have.
    */
    class recorder {
    public:
        /**
        * @brief Records that a hook ran, setting its bit and bumping its count.
        *
        * @param which The hook that ran. Passing more than one bit is meaningless
        *        here - each hook reports itself as it runs - so the counter
        *        attributed is the one belonging to `which` alone.
        */
        void ran(hook which) noexcept
        {
            _hooks = static_cast<std::uint8_t>(_hooks | which);
            bump(counter_for(which));
        }

        /**
        * @brief Clears the ledger for the next scenario.
        *
        * Scenarios are driven in sequence against one long-lived context tree,
        * so without this each trace would carry the previous scenario's hooks
        * and a hook that stopped firing would still show its bit set.
        */
        void reset() noexcept
        {
            _hooks = 0;
            _executions = 0;
            _pauses = 0;
            _resumes = 0;
            _arrivals = 0;
        }

        /// @brief The mask of hooks that have run. @return The `hook` bits, OR-ed.
        [[nodiscard]] std::uint8_t hooks() const noexcept { return _hooks; }

        /// @brief How many times `on_execute()` ran. @return The count, saturated at 255.
        [[nodiscard]] std::uint8_t executions() const noexcept { return _executions; }

        /// @brief How many times `on_pause()` ran. @return The count, saturated at 255.
        [[nodiscard]] std::uint8_t pauses() const noexcept { return _pauses; }

        /// @brief How many times `on_resume()` ran. @return The count, saturated at 255.
        [[nodiscard]] std::uint8_t resumes() const noexcept { return _resumes; }

        /**
        * @brief How many tasks were constructed in this scope.
        *
        * The instant tier's only observable: a command that leaves no reply and
        * no record is indistinguishable from one that never arrived, so its
        * constructor counting itself here is the entire proof that it ran.
        *
        * @return The count, saturated at 255.
        */
        [[nodiscard]] std::uint8_t arrivals() const noexcept { return _arrivals; }

    private:
        /**
        * @brief The counter a given hook increments, or none.
        *
        * A mapping rather than a chain of `if`s so that adding a hook is adding
        * a row. Hooks that fire at most once per task (`is_finished` is polled
        * repeatedly but says nothing by its count) carry no counter - their bit
        * in the mask is the whole story.
        *
        * @param which The hook that ran.
        * @return Pointer to the counter to bump, or `nullptr` if this hook is
        *         tracked by its bit alone.
        */
        [[nodiscard]] std::uint8_t* counter_for(hook which) noexcept
        {
            switch (which) {
                case hook::construct: return &_arrivals;
                case hook::execute:   return &_executions;
                case hook::pause:     return &_pauses;
                case hook::resume:    return &_resumes;
                default:              return nullptr;
            }
        }

        /**
        * @brief Increments a counter without letting it wrap.
        *
        * @param counter The counter to bump, or `nullptr` for a hook that has
        *        none - accepted rather than guarded against at every call site.
        */
        static void bump(std::uint8_t* counter) noexcept
        {
            // Wrapping would let a task that overran by exactly 256 report the
            // expected count, which is worse than reporting an obvious ceiling.
            if (counter and *counter < 255)
                ++*counter;
        }

        std::uint8_t _hooks{0};
        std::uint8_t _executions{0};
        std::uint8_t _pauses{0};
        std::uint8_t _resumes{0};
        std::uint8_t _arrivals{0};
    };

} // namespace support::lifecycle

#endif // SUPPORT_LIFECYCLE_RECORDER_HPP_
