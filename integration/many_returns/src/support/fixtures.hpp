/**
* @file fixtures.hpp
*
* @brief The exact values every task in this project returns.
*
* @note User-owned (support/). Not generated.
*
* ## Why the values live here rather than in the tasks
*
* A round-trip test is only as good as its expectations, and an expectation the
* firmware computes is not one - a task that returns `sensor.read()` can only be
* checked against "something arrived". So every task here returns a constant,
* and the constants sit in one header so the host driver's copy can be diffed
* against this file by eye rather than hunted through fourteen task bodies.
*
* ## Why these particular values
*
* Not 1, 2, 3. A codec bug is nearly always a width bug or a byte-order bug, and
* small round numbers survive both: byte-swap `1` in a uint32 and you get
* 16777216, which is wrong and obvious - but truncate it to a uint16 and you
* still get 1. So each integer here is chosen to fail loudly under exactly those
* two mistakes:
*
* - Every byte of a multi-byte value is distinct and non-zero, so a swap changes
*   the number and a truncation drops information rather than zeros.
* - The signed values are negative, because sign extension is the one integer
*   error that survives a correct width: -1 read as unsigned is 255, the right
*   byte and the wrong number.
* - The reals are not exactly representable at the other's width, so a float
*   silently widened to a double (or the reverse) perturbs the value instead of
*   preserving it.
*/
#ifndef SUPPORT_FIXTURES_HPP_
#define SUPPORT_FIXTURES_HPP_
#include <cstdint>

namespace support::fixtures {

    // --------------------------------------------------------------- unsigned

    /// @brief uint8 with both nibbles set and distinct.
    inline constexpr std::uint8_t u8 = 0xA5;
    /// @brief uint16 whose two bytes differ, so a swap is visible.
    inline constexpr std::uint16_t u16 = 0xBEEF;
    /// @brief uint32 with four distinct non-zero bytes.
    inline constexpr std::uint32_t u32 = 0xDEADBEEF;
    /// @brief uint64 with eight distinct non-zero bytes - the ascending nibble
    ///        pattern, so a partial read shows *which* half it took.
    inline constexpr std::uint64_t u64 = 0x0123456789ABCDEFULL;

    // ----------------------------------------------------------------- signed

    /// @brief int8 that is not -1: -1 is all-ones and so survives most errors.
    inline constexpr std::int8_t i8 = -0x5B;             // -91
    /// @brief int16, negative, bytes distinct.
    inline constexpr std::int16_t i16 = -0x4321;         // -17185
    /// @brief int32, negative, bytes distinct.
    inline constexpr std::int32_t i32 = -0x12345678;     // -305419896
    /// @brief int64, negative, near the far end of the range so a narrowing
    ///        read cannot produce it by accident.
    inline constexpr std::int64_t i64 = -0x0123456789ABCDEFLL;

    /// @brief The bare `int` spelling, kept distinct from @ref i32 so a test can
    ///        tell which of the two TypeMap entries produced a wrong value.
    inline constexpr std::int32_t plain_int = -0x0BADF00D;

    // ------------------------------------------------------------------ reals

    /**
    * @brief A float that is not exactly a double's rounding of a simple decimal.
    *
    * `float(pi)` and `double(pi)` differ in the low bits, so a float sent where
    * a double was expected (or read at the wrong width) shifts the value rather
    * than arriving intact.
    */
    inline constexpr float f32 = 3.14159274101257324f;

    /// @brief A double whose low bits are set, for the same reason as @ref f32.
    inline constexpr double f64 = -2.718281828459045235;

    // ------------------------------------------------------------------ bools

    /// @brief A true, to be read back as true.
    inline constexpr bool yes = true;
    /// @brief A false beside it: a codec that writes a constant would pass on
    ///        `yes` alone.
    inline constexpr bool no = false;

    // ----------------------------------------------------------- wide.telemetry

    /**
    * @brief The base of `wide.telemetry`'s fourteen doubles.
    *
    * The task returns `wide_base + i` for channel `i`, so every one of the
    * fourteen is a different number: a shape this wide is exactly where a
    * one-slot offset hides, and identical values would hide it completely.
    * Fractional so that a double truncated to a float is visibly not itself.
    */
    inline constexpr double wide_base = 1000.5;

    /// @brief How many doubles `wide.telemetry` returns; the widest shape here.
    inline constexpr int wide_channels = 14;

    // ------------------------------------------------------------- keyed tasks

    /// @brief `keyed.measure`'s `finished` reading.
    inline constexpr double measure_value = 12.25;
    /// @brief `keyed.measure`'s `finished` variance.
    inline constexpr double measure_variance = 0.0625;
    /// @brief `keyed.measure`'s `finished` sample count.
    inline constexpr std::uint16_t measure_samples = 0xC0DE;
    /// @brief The bus id `keyed.measure` names on its `task_io_error` branch.
    inline constexpr std::uint8_t measure_bus = 0x3C;

    /// @brief The iteration count `keyed.converge` reports on either branch.
    inline constexpr std::uint32_t converge_iterations = 0x11223344;
    /// @brief Whether `keyed.converge` had settled when it was aborted. False,
    ///        because a task force-completed mid-run has not settled - and a
    ///        false is the value a bool bug is likeliest to get wrong.
    inline constexpr bool converge_settled = false;

    /// @brief The label `keyed.classify` reports on both of its branches.
    inline constexpr std::uint8_t classify_label = 0x7E;
    /// @brief The confidence carried only on the custom branch.
    inline constexpr float classify_confidence = 0.87500f;
    /// @brief The detail word carried only on the custom branch.
    inline constexpr std::int64_t classify_detail = -0x7EDCBA9876543210LL;

} // namespace support::fixtures

#endif // SUPPORT_FIXTURES_HPP_
