/**
* @file exercise.cpp
*
* @brief Definition of the exercise.hpp api.
*
* @note User-owned support code, not generated.
*/
#include "support/exercise.hpp"
#include "support/witness.hpp"
#include "config/wiring.hpp"
#include <etools/memory/buffer_view.hpp>
#include <cstddef>

namespace support {

    namespace {

        /**
        * @brief Argument bytes handed to every task this project starts.
        *
        * Zeroed and generously sized. No task in this tree reads its arguments -
        * they exist in the schema so that the params machinery is exercised at
        * all - so the values do not matter, only that there are enough bytes for
        * the widest signature to unpack without the adapter refusing.
        */
        constexpr std::size_t payload_bytes = 32;
        const std::byte arguments[payload_bytes]{};

        /**
        * @brief Ticks allowed before a task is treated as stuck.
        *
        * Every task here concludes on its first `is_finished()`, so one tick is
        * enough and two is slack. A task still live after that has not been
        * slow; it has failed to conclude, and reporting zero witness entries is
        * how the driver learns that.
        */
        constexpr int max_ticks = 4;

    } // namespace

    result exercise(std::uint16_t uid)
    {
        witness::clear();

        const auto typed = static_cast<global::task_id>(uid);
        const auto status = config::internal.register_task(
            typed, etools::memory::buffer_view{arguments, payload_bytes});

        // Instant commands have already run and reported by now; managed ones
        // need ticks. Ticking regardless is harmless and keeps the two paths
        // from needing to be told apart here - which the caller could not do
        // anyway, since a uid does not carry its tier.
        for (int tick = 0; tick < max_ticks and witness::count == 0; ++tick) {
            config::manager.update();
        }

        return result{
            static_cast<std::uint8_t>(status),
            static_cast<std::uint16_t>(witness::count),
            witness::count > 0 ? witness::log[0].uid : std::uint16_t{0},
            witness::count > 0 ? static_cast<std::uint8_t>(witness::log[0].at) : std::uint8_t{0},
        };
    }

} // namespace support
