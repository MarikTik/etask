/**
* @file fold.hpp
*
* @brief The digest `wide.saturated` and `wide.folded_mixed` answer with.
*
* @note User-owned. Nothing here is generated: it is this project's own
*       helper, and it lives under support/ because two tasks share it and a
*       copy in each would be a second place for the two ends of the contract
*       to drift apart.
*
* ## Why a digest exists at all
*
* Every other task in this project echoes its arguments straight back, which
* is the strongest check available: the driver compares byte for byte and a
* failure names the field. Two tasks cannot do that. Their parameter lists are
* the widest the project declares, and echoing them would make the *reply*
* frame the widest too - which would change what those tasks measure, since
* they exist to push the request direction to its edge.
*
* So they fold instead. A digest over every argument's bytes keeps the check
* byte-exact - a truncation, a widening or a byte swap anywhere in the list
* changes it - and costs eight bytes of reply rather than forty-eight. What it
* gives up is localization: a mismatch says the list is wrong, not which field
* is. That is an acceptable trade only because the echo tasks already cover
* every type individually, so a digest failure with every echo passing points
* at length or ordering rather than at a type.
*
* ## Why FNV-1a
*
* Not for its distribution - this is not a hash table - but because it is
* trivially reproducible on the host. `verify.py`'s `fold()` is the normative
* description of what these functions compute, and the two must agree bit for
* bit; a construction any more elaborate would be a second thing to keep in
* step. It is also bit-sensitive in a way an arithmetic fold is not: summing
* or xoring the *values* lets a truncated double cancel against another, while
* mixing their bytes cannot.
*/
#ifndef SUPPORT_FOLD_HPP_
#define SUPPORT_FOLD_HPP_
#include <cstddef>
#include <cstdint>
#include <cstring>

namespace support::fold {

    /// @brief The 64-bit FNV-1a offset basis: the digest before anything is folded in.
    inline constexpr std::uint64_t offset_basis = 0xCBF29CE484222325ULL;

    /// @brief The 64-bit FNV prime the digest is multiplied by after each byte.
    inline constexpr std::uint64_t prime = 0x00000100000001B3ULL;

    /**
    * @brief Mixes one value's own wire bytes into a running digest.
    *
    * The bytes mixed in are `sizeof(T)` - the value's *declared* width, not
    * the width it would be promoted to in an expression. A `std::uint8_t`
    * contributes one byte here, and a device that had widened it on the way
    * through would contribute four and disagree. That is precisely the drift
    * an echo cannot show: an echo reveals what a value was, never how it was
    * held between being unpacked and being packed again.
    *
    * @tparam T The value's type. Must be trivially copyable, which every
    *         schema scalar is - the schema has no other kind of type.
    * @param digest The running digest; seed the first call with @ref offset_basis.
    * @param value The value whose object representation is folded in.
    * @return The digest with `value`'s bytes mixed in.
    */
    template<typename T>
    inline std::uint64_t fold_one(std::uint64_t digest, const T& value)
    {
        // memcpy into a local, rather than reading through a cast pointer. The
        // arguments these tasks receive are deliberately laid out at offsets
        // their own alignment does not divide, and on Xtensa an unaligned load
        // through a cast is a fault rather than a slow read - so the one bug
        // this project is hunting would show up as a crash whose cause is the
        // test harness rather than as a mismatch the driver can report.
        unsigned char bytes[sizeof(T)];
        std::memcpy(bytes, &value, sizeof(T));

        for (std::size_t i = 0; i < sizeof(T); ++i) {
            digest ^= static_cast<std::uint64_t>(bytes[i]);
            digest *= prime;
        }
        return digest;
    }

} // namespace support::fold

#endif // SUPPORT_FOLD_HPP_
