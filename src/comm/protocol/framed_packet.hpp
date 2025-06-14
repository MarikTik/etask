/**
* @file framed_packet.hpp
* @brief Definition of the framed packet structure for etask communication protocol with checksum support.
* 
* This file defines the `framed_packet` structure, which extends the basic packet format by 
* including an optional checksum field (FCS - Frame Check Sequence). The checksum type is fully 
* configurable via policy-based template parameterization.
* 
* The framed_packet ensures:
* - Word-aligned total packet size.
* - Precise memory layout suitable for embedded serialization.
* - Flexible integration of multiple checksum algorithms via ChecksumPolicy.
* 
* The structure is designed for safe transmission over unreliable links 
* such as serial, radio, or low-level networking layers.
*/

#ifndef FRAMED_PACKET_HPP_
#define FRAMED_PACKET_HPP_

#include <cstddef>
#include <cstdint>
#include "packet_header.hpp"
#include "checksum.hpp"

namespace etask::comm {
    #pragma pack(push, 1) // Ensure 1-byte packing for header and payload alignment
    /**
    * @struct framed_packet
    * @brief Full protocol packet structure with checksum protection.
    * 
    * The framed_packet extends the basic_packet by adding a final checksum field,
    * which provides data integrity verification for the header, task_id, and payload.
    * 
    * @tparam PacketSize The total size of the packet in bytes (including header, task ID, payload, and checksum). Must be word-aligned.
    * @tparam TaskID_UnderlyingType The underlying type used for task identifiers (e.g. uint8_t, uint16_t).
    * @tparam ChecksumPolicy The checksum algorithm to use (e.g. checksum::crc32, checksum::sum16, checksum::none).
    * 
    * Packet layout:
    * ```
    * +-----------------------+--------------+-------------------+--------------------+-------------|
    * |      header_t         |          task_id              |    payload   |    checksum (FCS)    |
    * +-----------------------+--------------+-------------------+--------------------+-------------|         
    * | sizeof(header_t)      | sizeof(TaskID_UnderlyingType) | payload_size | ChecksumPolicy::size |
    * +-----------------------+--------------+-------------------+--------------------+-------------|
    * ```
    */
    template<
    std::size_t PacketSize = 32,
        typename TaskID_UnderlyingType = std::uint8_t,
        typename ChecksumPolicy = checksum::crc32
    >
    struct framed_packet {
        
        /// Compile-time alignment enforcement: total packet must be word-aligned
        static_assert(PacketSize % sizeof(size_t) == 0, "Packet must be word-aligned.");
        
        /// Compile-time sanity check: packet size must fit at minimum header, task ID, and checksum
        static_assert(PacketSize >= sizeof(header_t) + sizeof(TaskID_UnderlyingType) + ChecksumPolicy::size,
        "Packet size must be at least the size of header, task ID, and checksum.");
        
        /// @brief Compile-time constant representing the payload size in bytes.
        static constexpr std::size_t payload_size = PacketSize - sizeof(header_t) - sizeof(TaskID_UnderlyingType) - ChecksumPolicy::size;
        
        /// @brief Compact packet header containing all protocol metadata.
        header_t header;
        
        /// @brief Task identifier assigned to this packet.
        TaskID_UnderlyingType task_id;
        
        /// @brief Payload data storage (automatically sized based on packet size and checksum).
        std::byte payload[payload_size]{};
        
        /// @brief Frame Check Sequence field for checksum integrity protection.
        typename ChecksumPolicy::value_type fcs;
    };
    #pragma pack(pop) // Restore previous packing alignment
} // namespace etask::comm

#endif // FRAMED_PACKET_HPP_
