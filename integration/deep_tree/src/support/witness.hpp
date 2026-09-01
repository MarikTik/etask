/**
* @file witness.hpp
*
* @brief The record of which task actually ran, for the host-side driver to read.
*
* @note User-owned support code, not generated. It exists only for this
*       integration project.
*
* ## Why a witness rather than the ordinary result path
*
* The question this project answers is whether two tasks the generator built
* from one abstract-scope definition - `mesh.s0.n0.p0.sample` and
* `mesh.s0.n0.p1.sample`, say - are genuinely two tasks. A result that came
* back could answer that, but two of the three answers this project needs
* cannot travel that way:
*
* - `etask::core::channels::internal_channel` runs a task's `on_complete`
*   against a discard scratch and drops what it packs (see its own docs: a
*   future `track_task` is to capture it). So a locally-started task's result
*   reaches nobody.
* - an `instant_task` has no `on_complete` at all. `quench` is one, and it is
*   72 of the tree's tasks - the largest single group of uids the instant
*   dispatcher owns, and the ones a routing mistake would most likely alias.
*
* So each task reports itself here instead, by the uid it was *compiled* with.
* That is the strongest available identity: it is `global::task_id::<path>`,
* fixed at compile time from the schema path, so a task that ran under another
* task's registration would report the wrong number rather than the right one.
*
* ## What it is not
*
* Not a channel, and not a general result mechanism. A real project delivers
* results over a link. This is a test fixture: a flat array in RAM that the
* driver reads back after driving the manager, sized for the whole tree at once
* so a run never silently truncates.
*/
#ifndef SUPPORT_WITNESS_HPP_
#define SUPPORT_WITNESS_HPP_
#include <cstddef>
#include <cstdint>

namespace support {

    /**
    * @brief Which lifecycle point a witness entry was recorded at.
    *
    * Recorded alongside the uid because the tiers reach the witness by
    * different routes - a managed task from `on_complete`, an instant command
    * from its constructor - and a driver that could not tell them apart could
    * not tell a missing completion from a command that ran.
    */
    enum class phase : std::uint8_t {
        /// @brief A managed task concluding: recorded from `on_complete`.
        completed = 1,
        /// @brief An instant command running: recorded from its constructor.
        ran = 2,
    };

    /**
    * @brief One task's report that it, specifically, executed.
    */
    struct entry {
        /// @brief The reporting task's `uid`, as compiled from its schema path.
        std::uint16_t uid;
        /// @brief Where in the task's life this was recorded.
        phase at;
    };

    /**
    * @brief The append-only log every task in this project reports itself to.
    *
    * A plain struct with static storage rather than a class with accessors: the
    * generated task bodies that write to it are the point of the project, and
    * they should read as one line that says what the task is, not as a call
    * into a fixture.
    */
    struct witness {
        /**
        * @brief Room for every task in the tree to report once, twice over.
        *
        * Sized generously on purpose. A run that overflowed would drop the
        * evidence of whatever ran last, which is the one thing this file exists
        * to preserve - so overflow is made unreachable for any plausible run
        * rather than merely detected. @ref overflowed still reports it, because
        * "unreachable" is a claim about today's driver, not a guarantee.
        */
        static constexpr std::size_t capacity = 1024;

        /// @brief The entries recorded so far, oldest first.
        static entry log[capacity];

        /// @brief How many entries have been recorded, capped at @ref capacity.
        static std::size_t count;

        /// @brief Whether any report was dropped for want of room.
        static bool overflowed;

        /**
        * @brief Records that the task owning @p uid reached @p at.
        *
        * @param uid The reporting task's compiled uid, as `global::task_id`
        *        narrowed to its underlying type by the caller.
        * @param at Which lifecycle point this is.
        */
        static void record(std::uint16_t uid, phase at) noexcept
        {
            if (count >= capacity) {
                overflowed = true;
                return;
            }
            log[count++] = entry{uid, at};
        }

        /**
        * @brief Forgets everything recorded so far.
        *
        * The driver runs many independent checks against one process, and each
        * wants to see only its own task's report.
        */
        static void clear() noexcept
        {
            count = 0;
            overflowed = false;
        }
    };

} // namespace support

#endif // SUPPORT_WITNESS_HPP_
