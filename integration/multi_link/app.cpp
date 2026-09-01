/**
* @file app.cpp
*
* @brief Your application's startup and per-tick logic.
*
* @note User-owned. This is where the app actually does things. It is a normal
*       translation unit (compiled once), so it is the right home for real logic -
*       unlike the header-only wiring in config/ that it draws on.
*
* Two links are serviced here, symmetrically. The symmetry is deliberate: every
* difference between `bench` and `net` - frame size, checksum, addressing, and
* which tasks each will accept - is declared in schema.yaml and enforced inside
* the channels. If this file had to treat them differently, the per-link machinery
* would not be doing its job.
*/
#include "app.hpp"
#include "config/wiring.hpp"
#include <etask/core/protocol/preamble.hpp>
#include <cstdio>

namespace app {

    namespace {

        /**
        * @brief Feeds one link its peer's handshake preamble, once it arrives.
        *
        * The channel does not read the preamble itself. It cannot: the preamble
        * is deliberately not a packet - two peers that disagree about header
        * layout could not exchange one - so `external_channel` exposes
        * `accept_handshake(bytes)` and leaves acquiring those bytes to whoever
        * owns the receive path. On a stream transport that is the transport.
        *
        * Polled every tick rather than awaited at startup, because a link may
        * come up late, drop, and come up again; a one-shot wait in `setup` would
        * leave the second connection permanently un-handshaken and therefore
        * permanently silent.
        *
        * @tparam Channel An `external_channel` instantiation.
        * @param channel The link to advance.
        * @param transport That link's transport, holding the receive buffer.
        */
        template<typename Channel>
        void advance_handshake(Channel& channel, support::channels::stream_channel& transport)
        {
            if (channel.is_ready()) return;

            std::byte preamble[etask::core::protocol::preamble::size];
            if (not transport.try_receive_raw(preamble, sizeof(preamble))) return;

            // The return is deliberately ignored rather than acted on: a mismatch
            // leaves this link not-ready, which already refuses every frame, and
            // the peer is told by *its* copy of this check. There is nothing this
            // side can usefully do differently, and a link that failed the
            // handshake must not start sending error frames a peer with a
            // different header layout would misparse.
            (void)channel.accept_handshake(preamble);
        }

        /**
        * @brief Reports this build's wire contract, once, on stderr.
        *
        * Exists for the host driver rather than for an operator: `verify.py`
        * asserts that the two links really did come out different sizes, and
        * the only authority on that is the binary it is about to talk to.
        */
        void announce()
        {
            // Printed rather than assumed by the host, because the frame sizes
            // are settled by the *compiler*: the generator emits a payload
            // requirement, and `packet_size_for` adds a header whose width only
            // the target knows. A host test that recomputed them would be
            // testing its own arithmetic; one that reads them back is testing
            // the build it is about to drive.
            //
            // On stderr, so it cannot be mistaken for link traffic - both links'
            // descriptors are elsewhere, and stdout stays free for a board port
            // to use as a console.
            std::fprintf(stderr,
                "etask-multi-link fingerprint=%016llX\n"
                "link bench request=%zu reply=%zu\n"
                "link net request=%zu reply=%zu\n",
                static_cast<unsigned long long>(generated::schema_fingerprint),
                sizeof(generated::links::bench::request_packet_t),
                sizeof(generated::links::bench::reply_packet_t),
                sizeof(generated::links::net::request_packet_t),
                sizeof(generated::links::net::reply_packet_t));
            std::fflush(stderr);
        }

    } // namespace

    void bind_links(int bench_fd, int net_fd)
    {
        config::bench_transport.bind(bench_fd);
        config::net_transport.bind(net_fd);
    }

    void setup()
    {
        announce();

        // Both peers announce their fingerprint immediately rather than waiting
        // to be spoken to. Symmetric, so neither side can hang waiting for the
        // other to open, and it costs one round trip instead of two.
        (void)config::bench.begin_handshake();
        (void)config::net.begin_handshake();
    }

    void loop()
    {
        advance_handshake(config::bench, config::bench_transport);
        advance_handshake(config::net, config::net_transport);

        // Each channel polls its own transport and dispatches at most one frame
        // per tick. Both are serviced every tick so neither link can starve the
        // other - a link saturated with traffic must not make the other appear
        // dead, which is precisely the failure a single shared channel would have.
        config::bench.update();
        config::net.update();

        config::manager.update();      // advance tasks, deliver results
    }

} // namespace app
