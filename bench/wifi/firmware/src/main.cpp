/**
* @file main.cpp
*
* @brief WiFi round-trip benchmark firmware: accepts etask requests over TCP and replies.
*
* @ingroup etask_bench
*
* The board half of bench/wifi/roundtrip.py. It brings up WiFi, listens on a TCP port, and runs an
* etask external channel over it - nothing else is attached, so the only things in the measurement
* are the network, ecomm's framing, and etask itself.
*
* Three oneshot tasks, matching the uids the PC harness sends:
*
*   0x20 echo  - completes immediately, no work. The PC subtracts this case from the others, so it
*                is the transport floor: WiFi latency plus ecomm framing plus one etask lifecycle.
*   0x21 light - ~20 flops before completing.
*   0x22 heavy - ~500 flops before completing.
*
* Plus one instant command (0x10) that sends **no reply** - the tier's contract. It is here so the
* firmware can be driven with `client.dispatch()` to measure one-way command throughput, where
* there is nothing to wait for.
*
* ## Configure before flashing
*
* WiFi credentials come from build flags, so they are not committed:
*
*   pio run -e esp32dev -t upload \
*     --project-option='build_flags=-DBENCH_SSID=\"my-net\" -DBENCH_PASS=\"secret\"'
*
* or edit platformio.ini. The board prints its IP over serial at 115200 baud on boot; pass that to
* roundtrip.py with --host.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-08-27
*
* @copyright
* MIT License
* SPDX-License-Identifier: MIT
*/
#include <Arduino.h>

#if defined(ESP32)
  #include <WiFi.h>
#else
  #include <ESP8266WiFi.h>
#endif

#include <ecomm/protocol/protocol.hpp>
#include <ecomm/channels/arduino_wifi_channel.hpp>
#include <etask/core/core.hpp>
#include <etools/meta/typelist.hpp>
#include <cstdint>

#ifndef BENCH_SSID
#define BENCH_SSID "set-BENCH_SSID"
#endif
#ifndef BENCH_PASS
#define BENCH_PASS "set-BENCH_PASS"
#endif
#ifndef BENCH_PORT
#define BENCH_PORT 3333
#endif

using namespace etask::core;

namespace {

    /// Must match the PacketSchema in roundtrip.py exactly: 32 bytes, network topology (so the
    /// reply can be addressed back to the PC), no checksum (TCP already guarantees integrity, and
    /// a CRC here would put ecomm's checksum cost into every measurement).
    using packet_t = ecomm::protocol::packet<
        32,
        ecomm::protocol::topology::network,
        ecomm::protocol::no_sequence,
        ecomm::protocol::none>;

    enum class task_id : std::uint8_t {
        instant_noop = 0x10,
        echo         = 0x20,
        light        = 0x21,
        heavy        = 0x22,
    };

    /// Sink, so the workloads below cannot be optimized away.
    volatile std::uint32_t sink = 0;

    /// ~20 flops. The same shape as the runtime suite's w1, so figures are comparable.
    inline std::uint32_t work_light(std::uint32_t i)
    {
        float acc = static_cast<float>(i);
        for (int k = 0; k < 5; ++k) acc = acc * 1.0009f + 0.5f;
        return static_cast<std::uint32_t>(acc);
    }

    /// ~500 flops. The runtime suite's w2.
    inline std::uint32_t work_heavy(std::uint32_t i)
    {
        float acc = static_cast<float>(i);
        for (int k = 0; k < 125; ++k) acc = acc * 1.0009f + 0.5f;
        return static_cast<std::uint32_t>(acc);
    }

    /// Counter, so each request's work differs and nothing can be hoisted or cached.
    std::uint32_t seq = 0;

    /// The transport floor: completes on its first tick, doing nothing.
    struct echo_task : polled_task<task_id> {
        static constexpr task_id uid = task_id::echo;
        explicit echo_task(etools::memory::buffer_view) {}
        void on_execute() override {}
        bool is_finished() override { return true; }
        outcome on_complete(completion_reason) override { return {++seq}; }
    };

    struct light_task : polled_task<task_id> {
        static constexpr task_id uid = task_id::light;
        std::uint32_t result = 0;
        explicit light_task(etools::memory::buffer_view) {}
        void on_execute() override { result = work_light(++seq); sink += result; }
        bool is_finished() override { return true; }
        outcome on_complete(completion_reason) override { return {result}; }
    };

    struct heavy_task : polled_task<task_id> {
        static constexpr task_id uid = task_id::heavy;
        std::uint32_t result = 0;
        explicit heavy_task(etools::memory::buffer_view) {}
        void on_execute() override { result = work_heavy(++seq); sink += result; }
        bool is_finished() override { return true; }
        outcome on_complete(completion_reason) override { return {result}; }
    };

    /// Fire-and-forget: runs inside the dispatch and sends nothing back.
    struct noop_command : instant_task {
        static constexpr task_id uid = task_id::instant_noop;
        explicit noop_command(etools::memory::buffer_view) { sink += ++seq; }
    };

    using manager_t = managers::task_manager_from_t<
        etools::meta::typelist<noop_command>,
        etools::meta::typelist<echo_task, light_task, heavy_task>,
        etools::meta::typelist<>>;

    manager_t manager{};

    WiFiServer server{BENCH_PORT};
    ecomm::channels::arduino_wifi_channel<0> link{server};

    channels::external_channel<packet_t, decltype(link), manager_t> external{link, manager};

} // namespace

void setup()
{
    Serial.begin(115200);
    delay(300);
    Serial.println();
    Serial.println("=== etask WiFi round-trip firmware ===");

    WiFi.mode(WIFI_STA);
    WiFi.begin(BENCH_SSID, BENCH_PASS);
    Serial.print("connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(250);
        Serial.print('.');
    }
    Serial.println();

    server.begin();

    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("TCP port:   ");
    Serial.println(BENCH_PORT);
    Serial.println();
    Serial.println("pass the IP above to: python3 bench/wifi/roundtrip.py --host <ip>");
    Serial.println("uids: 0x20 echo, 0x21 light, 0x22 heavy, 0x10 instant (no reply)");
}

void loop()
{
    // The whole hot path: pull one packet if there is one, dispatch it, then tick the managed
    // tasks. Nothing else runs on this board, so a round trip measures exactly this loop plus the
    // network.
    external.update();
    manager.update();
}
