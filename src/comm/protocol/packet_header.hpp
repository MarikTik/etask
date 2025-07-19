/**
* @file packet_header.hpp
*
* @brief Immutable packet packet_header definition for etask communication protocol.
*
* @ingroup etask_comm_protocol
*
* The packet packet_header occupies 24 bits and encodes metadata 
* required for packet routing, processing, and control.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-07-03
*
* @date 2025-07-14 Added `noexcept` specifier to methods for better exception safety.
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*
* @par Changelog
* - 2025-07-03 
*      - Initial creation.
* - 2025-07-14 
*      - Added `noexcept` specifier to methods for better exception safety.
* - 2025-07-15 
*      - Renamed `header_t` to `packet_header` for clarity.
*      - Renamed `flags_t` to `header_flags` for clarity.
*      - Added enum `header_type` to properly represent packet types. 
* - 2025-07-16
*      - Included a `receiver_id` byte field for devices to know intended packet recepient.
* - 2025-07-18
*      - Privatized `sender_id` field by setting it to default value of `ETASK_BOARD_ID` to ensure consistent sender ID usage across the protocol.
*/
#ifndef ETASK_COMM_PROTOCOL_PACKET_HEADER_HPP_
#define ETASK_COMM_PROTOCOL_PACKET_HEADER_HPP_
#include <cstdint>
#include "config.hpp"

namespace etask::comm::protocol{
    
    /**
    * @enum header_type
    * 
    * @brief Enumerates the different types of packet headers used in the protocol.
    */
    enum class header_type : uint8_t {
        data       = 0x0, ///< Generic application data packet
        config     = 0x1, ///< Configuration or parameter change
        control    = 0x2, ///< Protocol-level commands
        routing    = 0x3, ///< Routing or discovery
        time_sync  = 0x4, ///< Time synchronization message
        auth       = 0x5, ///< Authentication or login data
        session    = 0x6, ///< Session initiation/teardown
        status     = 0x7, ///< Device status or health info
        log        = 0x8, ///< Log or diagnostic data
        debug      = 0x9, ///< Debug-specific packets
        firmware   = 0xA, ///< Firmware updates or related payloads
        reserved_b = 0xB, ///< Reserved for future use
        reserved_c = 0xC, ///< Reserved for future use
        reserved_d = 0xD, ///< Reserved for future use
        reserved_e = 0xE, ///< Reserved for future use
        reserved_f = 0xF  ///< Reserved for future use
    };

    /**
    * @enum header_flags
    * 
    * @brief Control flags that may be embedded inside the packet packet_header.
    */
    enum class header_flags : uint8_t
    {
        none       = 0x0, ///< No flags
        ack        = 0x1, ///< Acknowledgment packet
        error      = 0x2, ///< Error indication
        heartbeat  = 0x3, ///< Heartbeat signal
        reserved_a = 0x4, ///< Reserved for future use
        reserved_b = 0x5, ///< Reserved for future use
        reserved_c = 0x6, ///< Reserved for future use
        reserved_d = 0x7  ///< Reserved for future use
    };
    
    #pragma pack(push, 1) // Ensure 1-byte packing for packet_header alignment
    /**
    * @class packet_header
    * @brief Compact 24-bit protocol packet_header for packet metadata transmission.
    *
    * Bit layout:
    * ```
    * 31-28 : Type (4 bits)
    * 27-26 : Version (2 bits)
    * 25    : Encrypted (1 bit)
    * 24    : Fragmentation (1 bit)
    * 23-21 : Priority (3 bits) (0 = no priority, higher = more important)
    * 20-18 : Flags (3 bits)
    * 17    : (Has) Checksum (1 bit)
    * 16    : Reserved (1 bit)
    * 15-8  : Sender ID (8 bits)
    * 7-0  : Receiver ID (8 bits)
    * ```
    */
    class packet_header {
    public:
        /// @brief Default constructor — zero-initialized packet_header
        inline packet_header() = default;
        
        /// @brief Construct directly from raw 16-bit packet_header value
        explicit inline packet_header(uint16_t raw_value, uint8_t receiver_id = 1) noexcept;

        /**
        * @brief Full field constructor.
        * 
        * Constructs a packet_header with all bit fields specified.
        * 
        * @param type Packet type (bits 23-20)
        * @param version Protocol version (bits 19-18)
        * @param encrypted Whether the packet is encrypted (bit 17)
        * @param fragmented Whether the packet is fragmented (bit 16)
        * @param priority Packet priority (bits 15-13, 0 = no priority)
        * @param flags Control flags (bits 12-10)
        * @param validated Whether the packet has a checksum (bit 9)
        * @param reserved Reserved bit (bit 8, default false)
        * 
        * Diagram of the packet_header layout:
        * ```
        * +-------------+---------+-----+------+-----------+----------+----------+----------+-----------------------+-----------------+
        * | 31 30 29 28 |  27 26  | 25  |  24  | 23 22 21  | 20 19 18 |    17    |    16    | 15 14 13 12 11 10 9 8 | 7 6 5 4 3 2 1 0 |
        * |    type     | version | enc | frag | priority  |  flags   | checksum | reserved | sender_id (immutable) |    receiver_id  |
        * +-------------+---------+-----+------+-----------+----------+----------+----------+-----------------------+-----------------+
        * ```
        */
        inline packet_header(
            header_type type,
            uint8_t version,
            bool encrypted,
            bool fragmented,
            uint8_t priority,
            header_flags flags,
            bool validated,
            bool reserved = false,
            uint8_t receiver_id = 1
        ) noexcept;
        
        /**
        * @brief Extract type field (bits 28-31).
        *
        * ```
        * +-------------+-----+
        * | 31 30 29 28 | ... |
        * |   type      | ... |
        * +-------------+-----+
        * 
        * @return The packet type as a header_type enum value.
        * ```
        */
        inline header_type type() const noexcept;
        
        /**
        * @brief Extract version field (bits 26-27).
        *
        * ```
        * +-----+---------+-----+
        * | ... |  27 26  | ... |
        * | ... | version | ... |
        * +-----+---------+-----+
        * ```
        */
        inline uint8_t version() const noexcept;
        
        /**
        * @brief Extract encrypted flag (bit 25).
        *
        * ```
        * +-----+-----+-----+
        * | ... |  25 | ... |
        * | ... | enc | ... |
        * +-----+-----+-----+
        * ```
        */
        inline bool encrypted() const noexcept;
        
        /**
        * @brief Extract fragmentation flag (bit 24).
        *
        * ```
        * +-----+------+-----+
        * | ... |  24  | ... |
        * | ... | frag | ... |
        * +-----+------+-----+
        * ```
        */
        inline bool fragmented() const noexcept;
        
        /**
        * @brief Extract priority field (bits 21-23).
        *
        * ```
        * +-----+----------+-----+
        * | ... | 23 22 21 | ... |
        * | ... | priority | ... |
        * +-----+----------+-----+
        * ```
        */
        inline uint8_t priority() const noexcept;
        /**
        * @brief Extract flags field (bits 18-20).
        *
        * ```
        * +-----+----------+-----+
        * | ... | 20 19 18 | ... |
        * | ... |   flags  | ... |
        * +-----+----------+-----+
        * ```
        */
        inline header_flags flags() const noexcept;

        /**
        * @brief Extract validation (checksum) presence flag (bit 17).
        *
        * ```
        * +-----+--------------+-----+
        * | ... |       17     | ... |
        * | ... | has_checksum | ... |
        * +-----+--------------+-----+
        * ```
        */
        inline bool validated() const noexcept;
        
        /**
        * @brief Extract reserved bit (bit 16).
        *
        * ```
        * +-----+----------+-----+
        * | ... |    16    | ... |
        * | ... | reserved | ... |
        * +-----+----------+-----+
        * ```
        */
        inline bool reserved() const noexcept;


        /**        
        * @brief Extract sender ID (bits 8-15).
        *
        * ```
        * +-----+-----------------------+-----+
        * | ... | 15 14 13 12 11 10 9 8 | ... |
        * | ... |       sender_id       | ... |
        * +-----+-----------------------+-----+
        * ```
        * @return The 8-bit sender ID.
        */
        inline uint8_t sender_id() const noexcept;
        
    private:
        /// @brief 16-bit space for the packet_header metadata
        std::uint16_t _space{}; 

        /**
        * @brief The 8 bit sender ID.
        *
        * Immutable; can be overridden by defining a custom value for `ETASK_BOARD_ID`.
        */
        std::uint8_t _sender_id{ETASK_BOARD_ID};

    public:
        /**
        * @brief The 8 bit receiver ID.
        * ```
        * +-----+----------------------+
        * | ... |   7 6 5 4 3 2 1 0    |
        * | ... |      receiver_id     |
        * +-----+----------------------+
        * ```
        */
        std::uint8_t receiver_id{};
    };
    #pragma pack(pop) // Restore previous packing alignment
    
} // namespace etask::comm::protocol

#include "packet_header.inl"
#endif // ETASK_COMM_PROTOCOL_PACKET_HEADER_HPP_