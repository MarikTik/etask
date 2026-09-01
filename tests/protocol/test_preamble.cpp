// tests/protocol/test_preamble.cpp
// SPDX-License-Identifier: MIT
//
// The handshake preamble is the one frame whose layout may never move: it is
// what two peers exchange *before* they know whether they agree about frame
// layout at all, so it cannot itself be described by the schema.
//
// `etask-python/tests/test_preamble.py` asserts the same bytes from the other
// side, against a literal captured from this implementation. Both files have to
// be wrong in the same way for a drift to go unnoticed, which is the point of
// having both.

#include <gtest/gtest.h>

#include <cstdint>
#include <cstring>

#include <etask/core/protocol/preamble.hpp>

namespace {

    using etask::core::protocol::preamble;
    using etask::core::protocol::preamble_error;

    /// A fingerprint whose every byte differs, so a byte-order bug cannot hide
    /// behind a palindrome.
    constexpr std::uint64_t kFingerprint = 0x71DD4EB1C4E0392DULL;

    /// The exact bytes the Python half expects. Copied from
    /// `etask-python/tests/test_preamble.py`; if the two ever disagree, the
    /// handshake fails in the field for a reason nobody can see.
    constexpr unsigned char kExpected[] = {
        0x45, 0x54, 0x53, 0x4B,                            // "ETSK"
        0x01,                                              // version
        0x00,                                              // reserved
        0x71, 0xDD, 0x4E, 0xB1, 0xC4, 0xE0, 0x39, 0x2D,    // fingerprint, big-endian
    };

    /// Encodes into a fresh buffer, so no test can see another's leftovers.
    struct encoded {
        std::byte bytes[preamble::size];

        explicit encoded(std::uint64_t fingerprint) noexcept
        {
            preamble::encode(bytes, fingerprint);
        }
    };

} // namespace

// ------------------------------------------------------------ the wire contract

TEST(Preamble, IsFourteenBytes)
{
    // Fixed forever: a peer reads this many bytes before it can know anything
    // else about the sender, so the number cannot be schema-dependent.
    EXPECT_EQ(preamble::size, 14u);
    EXPECT_EQ(sizeof(kExpected), preamble::size);
}

TEST(Preamble, MatchesThePythonEncodingByteForByte)
{
    const encoded frame{kFingerprint};
    EXPECT_EQ(std::memcmp(frame.bytes, kExpected, preamble::size), 0);
}

TEST(Preamble, LayoutIsWhereTheHeaderSaysItIs)
{
    const encoded frame{kFingerprint};
    const auto* raw = reinterpret_cast<const unsigned char*>(frame.bytes);

    EXPECT_EQ(std::memcmp(raw + preamble::magic_offset, "ETSK", preamble::magic_size), 0);
    EXPECT_EQ(raw[preamble::version_offset], preamble::version);
    EXPECT_EQ(raw[preamble::reserved_offset], 0u);
    EXPECT_EQ(preamble::read_fingerprint(frame.bytes), kFingerprint);
}

TEST(Preamble, FingerprintIsBigEndian)
{
    // So that a hex dump reads the same as the digest on either peer, and a log
    // line can be compared against a manual sha256sum by eye.
    const encoded frame{0x0123456789ABCDEFULL};
    const auto* raw = reinterpret_cast<const unsigned char*>(frame.bytes);

    const unsigned char want[] = {0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF};
    EXPECT_EQ(std::memcmp(raw + preamble::fingerprint_offset, want, sizeof(want)), 0);
}

TEST(Preamble, EncodeWritesEveryByte)
{
    // Documented to need no pre-clearing, so a caller's dirty buffer must not
    // leak into the frame.
    std::byte buffer[preamble::size];
    std::memset(buffer, 0xAB, sizeof(buffer));
    preamble::encode(buffer, kFingerprint);

    EXPECT_EQ(std::memcmp(buffer, kExpected, preamble::size), 0);
}

// ------------------------------------------------------------------- decoding

TEST(Preamble, AcceptsAMatchingPeer)
{
    const encoded frame{kFingerprint};
    std::uint64_t peer = 0;

    EXPECT_EQ(preamble::decode(frame.bytes, kFingerprint, &peer), preamble_error::none);
    EXPECT_EQ(peer, kFingerprint);
}

TEST(Preamble, RejectsADifferentSchemaAndReportsIt)
{
    constexpr std::uint64_t theirs = 0xDEADBEEFCAFEBABEULL;
    const encoded frame{theirs};
    std::uint64_t peer = 0;

    EXPECT_EQ(preamble::decode(frame.bytes, kFingerprint, &peer),
              preamble_error::fingerprint_mismatch);
    // The peer's value is the "actual" half of the log line, so a mismatch must
    // still hand it back - that is the whole diagnostic.
    EXPECT_EQ(peer, theirs);
}

TEST(Preamble, RejectsAForeignProtocol)
{
    std::byte frame[preamble::size]{};
    std::memcpy(frame, "HTTP/1.1 200 ", 13);

    EXPECT_EQ(preamble::decode(frame, kFingerprint), preamble_error::bad_magic);
}

TEST(Preamble, RejectsAnUnknownVersion)
{
    encoded frame{kFingerprint};
    frame.bytes[preamble::version_offset] = std::byte{0xFF};

    EXPECT_EQ(preamble::decode(frame.bytes, kFingerprint), preamble_error::bad_version);
}

TEST(Preamble, DoesNotReportAFingerprintItCouldNotTrust)
{
    // Eight bytes read out of a non-preamble are a random number that reads like
    // a real schema id; reporting one sends an operator hunting for a schema
    // that never existed. The out-param must be left exactly as it was.
    constexpr std::uint64_t untouched = 0x1111111111111111ULL;

    {
        std::byte frame[preamble::size]{};
        std::memcpy(frame, "XXXX", 4);
        std::uint64_t peer = untouched;
        EXPECT_EQ(preamble::decode(frame, kFingerprint, &peer), preamble_error::bad_magic);
        EXPECT_EQ(peer, untouched);
    }
    {
        encoded frame{kFingerprint};
        frame.bytes[preamble::version_offset] = std::byte{0xFF};
        std::uint64_t peer = untouched;
        EXPECT_EQ(preamble::decode(frame.bytes, kFingerprint, &peer),
                  preamble_error::bad_version);
        EXPECT_EQ(peer, untouched);
    }
}

TEST(Preamble, IgnoresTheReservedByte)
{
    // A future version may use it; refusing a non-zero value here would make
    // this build reject a peer it could otherwise talk to.
    encoded frame{kFingerprint};
    frame.bytes[preamble::reserved_offset] = std::byte{0x7F};

    EXPECT_EQ(preamble::decode(frame.bytes, kFingerprint), preamble_error::none);
}

TEST(Preamble, AcceptsANullOutParameter)
{
    // Documented as optional for a caller that only wants the verdict.
    const encoded frame{kFingerprint};
    EXPECT_EQ(preamble::decode(frame.bytes, kFingerprint, nullptr), preamble_error::none);
}

// ------------------------------------------------------------------ round trip

TEST(Preamble, RoundTripsEdgeValues)
{
    for (const std::uint64_t value : {std::uint64_t{0},
                                      std::uint64_t{1},
                                      std::uint64_t{0xFF},
                                      std::uint64_t{0xFFFFFFFF},
                                      ~std::uint64_t{0}}) {
        const encoded frame{value};
        std::uint64_t peer = 0;

        EXPECT_EQ(preamble::decode(frame.bytes, value, &peer), preamble_error::none)
            << "value " << value;
        EXPECT_EQ(peer, value) << "value " << value;
    }
}
