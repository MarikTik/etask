/**
* @file header.hpp
*
* @brief Immutable packet header definition for etask communication protocol.
*
* @ingroup etask_comm_protocol
*
* The packet header occupies 24 bits and encodes metadata 
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
* - 2025-07-03 Initial creation.
* - 2025-07-14 Added `noexcept` specifier to methods for better exception safety.
*/
#ifndef ETASK_COMM_PROTOCOL_PACKET_HEADER_HPP_
#define ETASK_COMM_PROTOCOL_PACKET_HEADER_HPP_
#include <cstdint>

namespace etask::comm::protocol{

    /**
    * @enum flags_t
    * @brief Control flags that may be embedded inside the packet header.
    */
    enum class flags_t : uint8_t
    {
        none      = 0b000, ///< No flags
        ack       = 0b001, ///< Acknowledgment packet
        error     = 0b010, ///< Error indication
        heartbeat = 0b011, ///< Heartbeat signal
        reserved  = 0b100  ///< Reserved for future use
    };
    
    #pragma pack(push, 1) // Ensure 1-byte packing for header alignment
    /**
    * @class header_t
    * @brief Compact 24-bit protocol header for packet metadata transmission.
    *
    * Bit layout:
    * ```
    * 23-20 : Type (4 bits)
    * 19-18 : Version (2 bits)
    * 17    : Encrypted (1 bit)
    * 16    : Fragmentation (1 bit)
    * 15-13 : Priority (3 bits) (0 = no priority, higher = more important)
    * 12-10 : Flags (3 bits)
    * 9     : (Has) Checksum (1 bit)
    * 8     : Reserved (1 bit)
    * 7-0  : Sender ID (8 bits) (0 = executing board device, 1-255 = control devices)
    * ```
    */
    class header_t {
    public:
        /// @brief Default constructor — zero-initialized header
        inline header_t() = default;
        
        /// @brief Construct directly from raw 16-bit header value
        explicit inline header_t(uint16_t raw_value, uint8_t sender_id = 0) noexcept;
        
        /**
        * @brief Full field constructor.
        * 
        * Constructs a header with all bit fields specified.
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
        * Diagram of the header layout:
        * ```
        * +-------------+---------+-----+------+-----------+----------+----------+----------+-----------------+
        * | 23 22 21 20 |  19 18  | 17  |  16  | 15 14 13  | 12 11 10 |    9     |     8    | 7 6 5 4 3 2 1 0 |
        * |   type      | version | enc | frag | priority  |  flags   | checksum | reserved |    sender_id    |
        * +-------------+---------+-----+------+-----------+----------+----------+----------+-----------------+
        * ```
        */
        inline header_t(
            uint8_t type,
            uint8_t version,
            bool encrypted,
            bool fragmented,
            uint8_t priority,
            flags_t flags,
            bool validated,
            bool reserved = false,
            uint8_t sender_id = 0
        ) noexcept;
        
        /**
        * @brief Extract type field (bits 15-12).
        *
        * ```
        * +-------------+-----+
        * | 23 22 21 20 | ... |
        * |   type      | ... |
        * +-------------+-----+
        * ```
        */
        inline uint8_t type() const noexcept;
        
        /**
        * @brief Extract version field (bits 11-10).
        *
        * ```
        * +-----+---------+-----+
        * | ... |  19 18  | ... |
        * | ... | version | ... |
        * +-----+---------+-----+
        * ```
        */
        inline uint8_t version() const noexcept;
        
        /**
        * @brief Extract encrypted flag (bit 9).
        *
        * ```
        * +-----+-----+-----+
        * | ... |  17 | ... |
        * | ... | enc | ... |
        * +-----+-----+-----+
        * ```
        */
        inline bool encrypted() const noexcept;
        
        /**
        * @brief Extract fragmentation flag (bit 8).
        *
        * ```
        * +-----+------+-----+
        * | ... |  16  | ... |
        * | ... | frag | ... |
        * +-----+------+-----+
        * ```
        */
        inline bool fragmented() const noexcept;
        
        /**
        * @brief Extract priority field (bits 7-5).
        *
        * ```
        * +-----+----------+-----+
        * | ... | 15 14 13 | ... |
        * | ... | priority | ... |
        * +-----+----------+-----+
        * ```
        */
        inline uint8_t priority() const noexcept;
        /**
        * @brief Extract flags field (bits 4-2).
        *
        * ```
        * +-----+----------+-----+
        * | ... | 12 11 10 | ... |
        * | ... |   flags  | ... |
        * +-----+----------+-----+
        * ```
        */
        inline flags_t flags() const noexcept;

        /**
        * @brief Extract validation (checksum) presence flag (bit 1).
        *
        * ```
        * +-----+--------------+-----+
        * | ... |       9      | ... |
        * | ... | has_checksum | ... |
        * +-----+--------------+-----+
        * ```
        */
        inline bool validated() const noexcept;
        
        /**
        * @brief Extract reserved bit (bit 0).
        *
        * ```
        * +-----+----------+-----+
        * | ... |     8    | ... |
        * | ... | reserved | ... |
        * +-----+----------+-----+
        * ```
        */
        inline bool reserved() const noexcept;
        
        /**
        * @brief Get the 8 bit sender ID.
        * ```
        * +-----+-----------------+
        * | ... | 7 6 5 4 3 2 1 0 |
        * | ... |     sender_id   |
        * +-----+-----------------+
        * ```
        */
        inline uint8_t sender_id() const noexcept;
    private:
        std::uint16_t _space{};
        uint8_t _sender_id{};
    };
    #pragma pack(pop) // Restore previous packing alignment
    
} // namespace etask::comm::protocol

#include "packet_header.inl"
#endif // ETASK_COMM_PROTOCOL_PACKET_HEADER_HPP_