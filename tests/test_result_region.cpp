// SPDX-License-Identifier: MIT
/**
* @file test_result_region.cpp
*
* @brief The three states a result region can be in, and what `outcome` does in
*        each - including which of them a debug build is entitled to abort on.
*
* These matter because the distinction is invisible at the call site: a task's
* `return {a, b}` is the same line whether its result is going onto a wire, into
* a discard, or nowhere at all because the task built it in the wrong place. The
* region it finds bound is the only thing that separates a correct completion
* from a programming error, so each state is pinned here.
*
* Built with asserts live (the suite does not define NDEBUG), so a test that
* trips an assert aborts and fails rather than quietly passing.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-09-02
*
* @copyright
* MIT License
* Copyright (c) 2026 Mark Tikhonov
* See LICENSE file for details.
*/
#include <gtest/gtest.h>

#include <etask/core/detail/result_region.hpp>
#include <etask/core/outcome.hpp>

#include <cstddef>
#include <cstdint>

using namespace etask::core;

namespace {

    /// A region with room: the ordinary wire case.
    TEST(ResultRegion, ABoundRegionTakesTheResult)
    {
        std::byte buffer[64]{};
        const detail::result_region_scope scope{buffer, sizeof(buffer)};

        const outcome result{std::uint32_t{7}, std::uint32_t{9}};

        EXPECT_EQ(result.status(), status_code::ok);
    }

    /// The discard region: bound, but with nowhere to put anything.
    ///
    /// A channel that drives `on_complete` with no destination - `internal_channel`
    /// - binds this. A task returning values there is behaving correctly; it is
    /// the channel that has nowhere to keep them. So the result must be reported
    /// as `result_too_large` and the debug assert must NOT fire: aborting here
    /// would mean a schema that runs fine over a link crashes the moment the same
    /// task is started locally.
    TEST(ResultRegion, TheDiscardRegionReportsRatherThanAborting)
    {
        const auto discard = detail::discard_region();
        const detail::result_region_scope scope{discard.data, discard.capacity};

        const outcome result{std::uint32_t{7}, std::uint32_t{9}};

        EXPECT_EQ(result.status(), status_code::result_too_large);
    }

    /// A task that returns nothing has nothing to not fit.
    TEST(ResultRegion, AnEmptyOutcomeThroughTheDiscardRegionIsFine)
    {
        const auto discard = detail::discard_region();
        const detail::result_region_scope scope{discard.data, discard.capacity};

        const outcome result{};

        EXPECT_EQ(result.status(), status_code::ok);
    }

    /// The discard region must be distinguishable from "no completion running".
    ///
    /// Both discard the bytes, but only one is a mistake - a null region means the
    /// task built its `outcome` outside `on_complete`, which the debug assert is
    /// there to catch. If the discard were simply null, that check would be lost
    /// for every internally-completed task.
    TEST(ResultRegion, TheDiscardRegionIsNotNull)
    {
        EXPECT_NE(detail::discard_region().data, nullptr);
        EXPECT_EQ(detail::discard_region().capacity, 0u);
    }

    /// The scope restores whatever was bound before it, so a nested completion
    /// cannot strand the outer one on the wrong destination.
    TEST(ResultRegion, ScopesRestoreThePreviousRegion)
    {
        std::byte outer[32]{};
        {
            const detail::result_region_scope scope{outer, sizeof(outer)};
            ASSERT_EQ(detail::current_result_region.data, outer);
            {
                const auto discard = detail::discard_region();
                const detail::result_region_scope inner{discard.data, discard.capacity};
                EXPECT_NE(detail::current_result_region.data, outer);
            }
            EXPECT_EQ(detail::current_result_region.data, outer);
            EXPECT_EQ(detail::current_result_region.capacity, sizeof(outer));
        }
        EXPECT_EQ(detail::current_result_region.data, nullptr);
    }

} // namespace
