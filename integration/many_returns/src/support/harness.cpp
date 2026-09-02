/**
* @file harness.cpp
*
* @brief The scripted request sequence, and the reply frames it produces.
*
* @note User-owned (support/). Not generated. See harness.hpp for what this is
*       for and why it lives beside the firmware.
*/
#include "support/harness.hpp"

#include <cstddef>
#include <cstdio>

#include "config/wiring.hpp"
#include "generated/task_id.hpp"
#include "support/fixtures.hpp"
#include "support/request_builder.hpp"

namespace support {

    namespace {

        /// @brief The builder for this project's one link.
        using builder = request_builder<
            generated::links::bench::request_packet_t, global::task_id>;

        /**
        * @brief Prints one tagged reply frame, or an empty one if none came back.
        *
        * The whole packet is printed - header included - rather than just the
        * payload. The header is where the frame's own size and checksum live, and
        * a driver that only ever saw payloads could not tell a truncated frame
        * from a short result.
        *
        * @param tag The case's name; the driver matches on it, so it must be
        *        unique across the run and must not contain a space.
        */
        /**
        * @brief Completes the link's schema handshake against itself.
        *
        * `external_channel::complete()` drops every reply while `is_ready()` is
        * false, and a link generated from a schema carries a fingerprint, so it
        * stays false until a preamble has been exchanged. Both ends here are this
        * process, so the exchange is with ourselves - but it has to be performed,
        * not assumed.
        *
        * `begin_handshake()` is deliberately not used: it writes the preamble
        * through `Hub::send`, whose signature on this harness's loopback hub takes
        * a `ReplyPacket` rather than the 14-byte preamble frame, so it does not
        * compile against it. The preamble is built directly and fed to
        * `accept_handshake` instead, which is the same bytes by the same encoder.
        */
        void handshake()
        {
            std::byte preamble[etask::core::protocol::preamble::size]{};
            etask::core::protocol::preamble::encode(
                preamble, generated::schema_fingerprint);
            (void)config::external.accept_handshake(preamble);
        }

        void print_reply(const char* tag)
        {
            const auto& sent = config::hub.sent();
            std::printf("case %s ", tag);
            // Exactly one reply per case is the contract; more than one means an
            // earlier case leaked into this one, and printing them all lets the
            // driver say so instead of silently reading the first.
            for (const auto& packet : sent) {
                const auto* bytes = reinterpret_cast<const unsigned char*>(&packet);
                for (std::size_t i = 0; i < sizeof(packet); ++i)
                    std::printf("%02X", bytes[i]);
            }
            std::printf("\n");
            config::hub.clear_sent();
        }

        /**
        * @brief Delivers one request and runs the system until it has answered.
        *
        * A fixed tick count rather than "until a reply arrives": a case that
        * produces no reply has to terminate too, and one that produces none when
        * it should is exactly the failure worth catching. Sixteen ticks is far
        * more than any task here needs - the only one that does not finish in its
        * first tick is `keyed.converge`, which never finishes at all.
        *
        * @param request The frame to feed the channel.
        */
        void deliver(const generated::links::bench::request_packet_t& request)
        {
            config::hub.deliver(request);
            for (int tick = 0; tick < 16; ++tick) {
                config::external.update();
                config::manager.update();
            }
        }

        /**
        * @brief Runs one case end to end: deliver, settle, print.
        *
        * @param tag The case's name in the transcript.
        * @param request The frame that starts it.
        */
        void run_case(
            const char* tag,
            const generated::links::bench::request_packet_t& request)
        {
            deliver(request);
            print_reply(tag);
        }

    } // namespace

    void harness::scalars()
    {
        // No arguments on any of these: what is under test is the reply, and a
        // parameter list would only add a second thing that could be wrong.
        run_case("unsigned_widths",
                 builder::start(global::task_id::scalars_unsigned_widths));
        run_case("signed_widths",
                 builder::start(global::task_id::scalars_signed_widths));
        run_case("plain_int", builder::start(global::task_id::scalars_plain_int));
        run_case("reals", builder::start(global::task_id::scalars_reals));
        run_case("flags", builder::start(global::task_id::scalars_flags));
        run_case("positional", builder::start(global::task_id::scalars_positional));
    }

    void harness::nothing()
    {
        // The no-`returns:` task. Its reply must still arrive, carrying the
        // manager's own task_finished and an empty result.
        run_case("acknowledge", builder::start(global::task_id::nothing_acknowledge));

        // Two empty shapes that differ only in their status byte, so the driver
        // can prove the discriminator moves independently of the values.
        run_case("report_io_error",
                 builder::start(global::task_id::nothing_report_status,
                                static_cast<std::uint8_t>(0)));
        run_case("report_timeout",
                 builder::start(global::task_id::nothing_report_status,
                                static_cast<std::uint8_t>(1)));
    }

    void harness::wide()
    {
        // The shape `reply_payload_need` was computed from. If the frame were
        // sized for anything narrower, `outcome` would refuse the pack and this
        // reply would come back as `result_too_large` with no bytes - which is
        // precisely what the driver asserts is *not* the case.
        run_case("telemetry", builder::start(global::task_id::wide_telemetry));
    }

    void harness::keyed()
    {
        // All three of `measure`'s branches, widest to empty.
        run_case("measure_finished",
                 builder::start(global::task_id::keyed_measure,
                                static_cast<std::uint8_t>(0)));
        run_case("measure_io_error",
                 builder::start(global::task_id::keyed_measure,
                                static_cast<std::uint8_t>(1)));
        run_case("measure_timeout",
                 builder::start(global::task_id::keyed_measure,
                                static_cast<std::uint8_t>(2)));

        // `converge` is two requests, not one: it never finishes on its own, so
        // starting it produces no reply at all and the reply only comes when it
        // is force-completed. Both halves are printed, because "the start
        // produced nothing" is itself part of what makes the abort branch the
        // reachable one.
        config::hub.deliver(builder::start(global::task_id::keyed_converge,
                                           support::fixtures::i32));
        deliver(builder::complete(global::task_id::keyed_converge,
                                  etask::core::completion_reason::aborted));
        print_reply("converge_aborted");

        // The custom status, and the ordinary completion beside it. Both open
        // with the same field, so only the status distinguishes them.
        run_case("classify_finished",
                 builder::start(global::task_id::keyed_classify,
                                static_cast<std::uint8_t>(0)));
        run_case("classify_custom",
                 builder::start(global::task_id::keyed_classify,
                                static_cast<std::uint8_t>(1)));
    }

    void harness::run()
    {
        // Agree the schema contract with ourselves before any request.
        //
        // `external_channel::complete()` refuses to send while `is_ready()` is
        // false, and `is_ready()` is false on a link that declares a fingerprint
        // until the preamble exchange has happened. `bench` is generated from a
        // schema, so it *does* carry one - which means without this the tasks all
        // run and conclude correctly and every reply is dropped on the way out,
        // reported by the driver as "the task never completed, or never started".
        //
        // A real peer sends its preamble and receives one back. Here both ends are
        // this process, so the local preamble is fed straight back into
        // accept_handshake: the exchange is with ourselves, which is exactly the
        // no-op the wiring comment describes, but it has to actually be performed
        // rather than assumed.
        handshake();

        // The frame sizes come first, because every later assertion is read
        // against them: a driver that decoded a 40-byte reply as if it were 128
        // would fail on the values and blame the codec.
        std::printf("reply_payload_need %zu\n",
                    generated::links::bench::reply_payload_need);
        std::printf("reply_packet_size %zu\n",
                    sizeof(generated::links::bench::reply_packet_t));
        std::printf("reply_payload_size %zu\n",
                    generated::links::bench::reply_packet_t::payload_size);
        std::printf("uid_bytes %zu\n", sizeof(global::task_id));

        scalars();
        nothing();
        wide();
        keyed();

        // A terminator, so a driver can tell a run that ended from one that died
        // part-way through. Without it a crash after the last case it happened to
        // check would read as a pass.
        std::printf("done\n");
    }

} // namespace support
