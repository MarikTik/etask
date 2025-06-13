/**
* @file basic_packet.hpp
* @brief Definition of the basic fixed-size packet structure for etask communication protocol.
*
* This file defines the minimal packet structure (`basic_packet`) used for encoding and decoding 
* messages exchanged between systems in the etask framework. 
* 
* A basic_packet consists of:
* - A compact header (etask::comm::header_t) which encodes protocol metadata
* - A task identifier (user-defined underlying type)
* - A fixed-size payload region
*
* The structure ensures word-alignment for efficient transmission, parsing, and embedded processing.
*/

#ifndef BASIC_PACKET_HPP_
#define BASIC_PACKET_HPP_

#include <cstdint>
#include <cstddef>
#include "packet_header.hpp"

namespace etask::comm {
    #pragma pack(push, 1) // Ensure 1-byte packing for header and payload alignment
    /**
    * @struct basic_packet
    * @brief Core packet structure for etask communication without checksum framing.
    * 
    * @tparam PacketSize The total size of the packet in bytes (including header, task_id, and payload). Must be word-aligned.
    * @tparam TaskID_UnderlyingType The underlying type used for task identifiers (e.g. uint8_t, uint16_t).
    * 
    * Packet layout:
    * ```
    * +-----------------------+-------------------------------+-------------------+
    * |      header_t         |             task_id           |      payload      |
    * +-----------------------+-------------------------------+-------------------+
    * | sizeof(header_t)      | sizeof(TaskID_UnderlyingType) |   payload_size    |
    * +-----------------------+-------------------------------+-------------------+
    * ```
    *
    * The payload size is computed automatically to fit the remaining space.
    */
    template<
        std::size_t PacketSize = 32,
        typename TaskID_UnderlyingType = std::uint8_t
    >
    struct basic_packet {
        /// Compile-time alignment enforcement: total packet must be word-aligned
        static_assert(PacketSize % sizeof(size_t) == 0, "Packet must be word-aligned.");
        
        /// Compile-time sanity check: packet size must fit at minimum header and task ID
        static_assert(PacketSize >= sizeof(header_t) + sizeof(TaskID_UnderlyingType),
        "Packet size must be at least the size of header and task ID.");
        
        /// @brief Compact packet header containing all protocol metadata.
        header_t header;
        
        /// @brief Task identifier assigned to this packet.
        TaskID_UnderlyingType task_id;
        
        /// @brief Payload data storage (automatically sized based on packet size).
        std::byte payload[payload_size]{};
        
        /// @brief Compile-time constant representing the payload size in bytes.
        static constexpr std::size_t payload_size = PacketSize - sizeof(header_t) - sizeof(TaskID_UnderlyingType); 
    };
    #pragma pack(pop) // Restore previous packing alignment
} // namespace etask::comm

#endif // BASIC_PACKET_HPP_
