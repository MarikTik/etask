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

#ifndef PROTOCOL_BASIC_PACKET_HPP_
#define PROTOCOL_BASIC_PACKET_HPP_

#include <cstdint>
#include <cstddef>
#include "packet_header.hpp"

namespace etask::comm::protocol {
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
    * +-----------------------+---------------------+-------------------------------+-------------------+
    * |      header_t         |     status_code     |            task_id            |      payload      |
    * +-----------------------+---------------------+-------------------------------+-------------------+
    * | sizeof(header_t)      |       1 byte        | sizeof(TaskID_UnderlyingType) |   payload_size    |
    * +-----------------------+---------------------+-------------------------------+-------------------+
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
        static_assert(PacketSize >= sizeof(header_t) + sizeof(TaskID_UnderlyingType) + 1,
        "Packet size must be at least the size of header and task ID.");
        
        ///@brief Default constructor — zero-initialized packet
        basic_packet() = default; 
        
        /// @brief Compile-time constant representing the total packet size in bytes.
        static constexpr std::size_t packet_size = PacketSize;
        
        /// @brief Compile-time constant representing the payload size in bytes.
        static constexpr std::size_t payload_size = PacketSize - sizeof(header_t) - sizeof(TaskID_UnderlyingType) - 1; 
        /** 
        * @brief Constructs a basic_packet with specified header and task ID. 
        * @param header The packet header containing protocol metadata.
        * @param task_id The task identifier assigned to this packet.
        * @note The payload is automatically zero-initialized.
        */
        inline basic_packet(header_t header, TaskID_UnderlyingType task_id, uint8_t status_code = 0);
        
        /**
        * @brief Constructs a basic_packet with specified header, task ID, and payload.
        * @param header The packet header containing protocol metadata.
        * @param task_id The task identifier assigned to this packet.
        * @param payload An array of bytes to initialize the payload.
        */
        inline basic_packet(header_t header, TaskID_UnderlyingType task_id, uint8_t status_code, const std::byte *payload, size_t payload_size);
        
        /// @brief Compact packet header containing all protocol metadata.
        header_t header;
        
        /// @brief Status code for the packet, if applicable (e.g. error codes).
        uint8_t status_code{}; 

        /// @brief Task identifier assigned to this packet.
        TaskID_UnderlyingType task_id;
        
        /// @brief Payload data storage (automatically sized based on packet size).
        std::byte payload[payload_size]{};
    };
    #pragma pack(pop) // Restore previous packing alignment
    
    /// @brief Predefined acknowledgment packet with default header and empty task ID.
    inline basic_packet<16> ackp {
        header_t{
            0, // type
            0, // version
            false, // encrypted
            false, // fragmented
            0,     // priority
            flags_t::ack, // flags
            false   // validated
        },
        0 // empty task ID for acknowledgment packets
    };
    
    /// @brief Predefined error packet with default header and empty task ID.
    inline basic_packet<16> errp {
        header_t{
            0, // type
            0, // version
            false, // encrypted
            false, // fragmented
            0,     // priority
            flags_t::error, // flags
            false   // validated
        },
        0 // empty task ID for error packets
    };
    
    /// @brief Predefined heartbeat packet with default header and empty task ID.
    inline basic_packet<16> hbp{
        header_t{
            0,                  // type
            0,                  // version
            false,              // encrypted
            false,              // fragmented
            0,                  // priority
            flags_t::heartbeat, // flags
            false               // validated
        },
        0 // empty task ID for heartbeat packets
    };
} // namespace etask::comm::protocol

#include "basic_packet.tpp"
#endif // BASIC_PACKET_HPP_
