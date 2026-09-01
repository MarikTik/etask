/**
* @file capturing_channel.hpp
*
* @brief A `channel` that keeps what a concluding task produced, so the host can
*        assert on it.
*
* @note User-owned. The generator never writes here.
*
* ## Why this exists rather than `internal_channel`
*
* `etask::core::channels::internal_channel` is the natural origin for tasks a
* node starts itself, and it is where this project would otherwise register
* everything - but it **discards** the result: it points `on_complete` at a
* scratch region precisely so the task packs as it would on the wire, then drops
* the bytes (a future `track_task` is the documented place that will change).
*
* That is the right default for a device running its own errands, and useless
* here. Half of what this project asserts is carried *in* the result:
*
* - the status the manager chose - `task_finished` against `task_aborted`
*   against `task_completed_early` - which is how the tier reports the manner of
*   an ending;
* - the `completion_reason` the task was handed, echoed back in its trace, which
*   is the only evidence a caller's reason reached `on_complete` intact rather
*   than being flattened on the way.
*
* Neither survives a channel that throws the reply away. So this channel keeps
* the region instead of discarding it, and hands back what landed there.
*
* It is also the smaller of the two honest options: the alternative is a real
* `external_channel` over a loopback transport, which would drag the whole
* packet/link layer into a test whose subject is the lifecycle. `multi_link` in
* project/ci-plan.md owns the wire; this project owns the hooks.
*/
#ifndef SUPPORT_LIFECYCLE_CAPTURING_CHANNEL_HPP_
#define SUPPORT_LIFECYCLE_CAPTURING_CHANNEL_HPP_
#include <etask/core/channel.hpp>
#include <etask/core/detail/result_region.hpp>
#include <etask/core/outcome.hpp>
#include <etask/core/status_code.hpp>
#include <array>
#include <cstddef>
#include <cstdint>

namespace support::lifecycle {

    /**
    * @class capturing_channel
    *
    * @brief Records every completion delivered to it: uid, status, and the
    *        result bytes the task packed.
    *
    * One reply is kept at a time - the last one - because the scenarios are
    * driven in sequence and each is read before the next begins. A queue would
    * only make it possible to assert against a reply from two scenarios ago
    * while believing it was the current one.
    *
    * @tparam Manager The `task_manager<...>` instantiation this channel serves.
    *         Named only for its `task_uid_t`; unlike `internal_channel` this one
    *         forwards nothing, so it holds no reference to a manager at all.
    * @tparam ResultBytes Size of the region a completing task packs into. Must
    *         be at least the largest result any task delivered here returns, or
    *         `outcome` refuses to pack (and asserts in debug) - see
    *         @ref etask::core::status_code::result_too_large.
    */
    template<typename Manager, std::size_t ResultBytes = 64>
    class capturing_channel : public etask::core::channel<typename Manager::task_uid_t> {
    public:
        /// @brief The task identifier type, taken from the manager.
        using task_uid_t = typename Manager::task_uid_t;

        /**
        * @brief Takes the result region, runs `on_complete`, and keeps what landed.
        *
        * The same sequence `internal_channel` performs, less the discarding: the
        * region is designated first so the task's `return {...}` packs into it
        * directly - no heap and no copy, exactly as on the wire - and only then
        * is the region read back.
        *
        * @param initiator_id Who asked for the task. Recorded for completeness;
        *        every scenario here is initiated by this node.
        * @param uid    The concluding task.
        * @param code   The manager's status for the ending. Kept as it arrives:
        *        a task that named its own status via `with_status` overrides it
        *        below, and which of the two won is itself an assertion.
        * @param reason Why the task is concluding; forwarded to `on_complete`.
        * @param t      The concluding task, invoked through its base.
        */
        void complete(
            std::uint8_t initiator_id,
            task_uid_t uid,
            etask::core::status_code code,
            etask::core::completion_reason reason,
            etask::core::task<task_uid_t>& t) override
        {
            _bytes.fill(std::byte{0});

            etask::core::detail::result_region_scope region{_bytes.data(), _bytes.size()};
            const etask::core::outcome produced = t.on_complete(reason);

            _initiator_id = initiator_id;
            _uid = uid;
            _size = produced.size();

            // `ok` is `outcome`'s "the task named no status" sentinel, so the
            // manager's own code stands in that case. Resolving it here rather
            // than at the assertion keeps the precedence rule in one place.
            _status = (produced.status() == etask::core::status_code::ok) ? code : produced.status();

            ++_completions;
        }

        /**
        * @brief Forgets the last reply, so a scenario cannot read the previous one.
        *
        * A stale reply is the failure this guards: a task that concluded when it
        * should not have, and one that failed to conclude at all, both leave the
        * captured reply untouched - and without clearing, the second is
        * indistinguishable from success.
        */
        void reset() noexcept
        {
            _completions = 0;
            _size = 0;
            _status = etask::core::status_code::ok;
        }

        /// @brief How many completions have been delivered since the last reset.
        /// @return The count. Anything but 1 per scenario is itself a failure.
        [[nodiscard]] std::size_t completions() const noexcept { return _completions; }

        /// @brief The status on the last reply. @return The task's chosen status,
        ///        or the manager's when the task named none.
        [[nodiscard]] etask::core::status_code status() const noexcept { return _status; }

        /// @brief The uid of the last task to conclude. @return Its identifier.
        [[nodiscard]] task_uid_t uid() const noexcept { return _uid; }

        /// @brief How many result bytes the last task packed. @return The size.
        [[nodiscard]] std::size_t size() const noexcept { return _size; }

        /**
        * @brief One byte of the last result, by position.
        *
        * Byte-addressed rather than typed, because every field this project's
        * schema returns is a `uint8`, and reading them positionally is what the
        * host does with the reply anyway - so a typed accessor would add a
        * decoding step that could itself be wrong.
        *
        * @param index Which byte, in wire order. Out of range yields 0 rather
        *        than reading past the packed result.
        * @return The byte, or 0 if `index` is beyond what was packed.
        */
        [[nodiscard]] std::uint8_t byte(std::size_t index) const noexcept
        {
            return index < _size ? static_cast<std::uint8_t>(_bytes[index]) : 0;
        }

    private:
        std::array<std::byte, ResultBytes> _bytes{};
        std::size_t _completions{0};
        std::size_t _size{0};
        std::uint8_t _initiator_id{0};
        task_uid_t _uid{};
        etask::core::status_code _status{etask::core::status_code::ok};
    };

} // namespace support::lifecycle

#endif // SUPPORT_LIFECYCLE_CAPTURING_CHANNEL_HPP_
