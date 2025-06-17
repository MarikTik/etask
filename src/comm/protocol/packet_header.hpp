/**
* @file header.hpp
* @brief Immutable packet header definition for etask communication protocol.
*
* The packet header occupies 16 bits and encodes metadata 
* required for packet routing, processing, and control.
*/
#ifndef PROTOCOL_PACKET_HEADER_HPP_
#define PROTOCOL_PACKET_HEADER_HPP_
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
    
    /**
    * @class header_t
    * @brief Compact 16-bit protocol header for framed packets.
    *
    * Bit layout:
    * ```
    * 15-12 : Type (4 bits)
    * 11-10 : Version (2 bits)
    * 9     : Encrypted (1 bit)
    * 8     : Fragmentation (1 bit)
    * 7-5   : Priority (3 bits) (0 = no priority, higher = more important)
    * 4-2   : Flags (3 bits)
    * 1-0   : Reserved (2 bits)
    * ```
    */
    class header_t {
    public:
        /// @brief Default constructor — zero-initialized header
        inline header_t() = default;
        
        /// @brief Construct directly from raw 16-bit header value
        explicit inline header_t(uint16_t raw_value);
        
        /**
        * @brief Full field constructor.
        * 
        * Constructs a header with all bit fields specified.
        * 
        * @param type Packet type (bits 15-12)
        * @param version Protocol version (bits 11-10)
        * @param encrypted Whether the packet is encrypted (bit 9)
        * @param fragmented Whether the packet is fragmented (bit 8)
        * @param priority Packet priority (bits 7-5, 0 = no priority)
        * @param flags Control flags (bits 4-2)
        * @param validated Whether the packet has a checksum (bit 1)
        * @param reserved Reserved bit (bit 0, default false)
        * 
        * Diagram of the header layout:
        * ```
        * +-------------+---------+-----+------+----------+-------+----------+----------+
        * | 15 14 13 12 |  11 10  |  9  |  8   |   7 6 5  | 4 3 2 |    1     |     0    |
        * |   type      | version | enc | frag | priority | flags | checksum | reserved |
        * +-------------+---------+-----+------+----------+-------+----------+----------+
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
            bool reserved = false
        );
        
        /**
        * @brief Extract type field (bits 15-12).
        *
        * ```
        * +-------------+-----+
        * | 15 14 13 12 | ... |
        * |   type      | ... |
        * +-------------+-----+
        * ```
        */
        inline uint8_t type() const;
        
        /**
        * @brief Extract version field (bits 11-10).
        *
        * ```
        * +-----+---------+-----+
        * | ... |  11 10  | ... |
        * | ... | version | ... |
        * +-----+---------+-----+
        * ```
        */
        
        inline uint8_t version() const;
        
        /**
        * @brief Extract encrypted flag (bit 9).
        *
        * ```
        * +-----+-----+-----+
        * | ... |  9  | ... |
        * | ... | enc | ... |
        * +-----+-----+-----+
        * ```
        */
        inline bool encrypted() const;
        
        /**
        * @brief Extract fragmentation flag (bit 8).
        *
        * ```
        * +-----+------+-----+
        * | ... |  8   | ... |
        * | ... | frag | ... |
        * +-----+------+-----+
        * ```
        */
        inline bool fragmented() const;
        
        /**
        * @brief Extract priority field (bits 7-5).
        *
        * ```
        * +-----+----------+-----+
        * | ... |   7 6 5  | ... |
        * | ... | priority | ... |
        * +-----+----------+-----+
        * ```
        */
        inline uint8_t priority() const;
        /**
        * @brief Extract flags field (bits 4-2).
        *
        * ```
        * +-----+-------+-----+
        * | ... | 4 3 2 | ... |
        * | ... | flags | ... |
        * +-----+-------+-----+
        * ```
        */
        inline flags_t flags() const;

        /**
        * @brief Extract validation (checksum) presence flag (bit 1).
        *
        * ```
        * +-----+--------------+-----+
        * | ... |       1      | ... |
        * | ... | has_checksum | ... |
        * +-----+--------------+-----+
        * ```
        */
        inline bool validated() const;
        
        /**
        * @brief Extract reserved bit (bit 0).
        *
        * ```
        * +-----+----------+
        * | ... |     0    |
        * | ... | reserved |
        * +-----+----------+
        * ```
        */
        inline bool reserved() const;

        /**
        * @brief Return raw packed 16-bit header word.
        */
        inline uint16_t raw() const;
        
    private:
        std::uint16_t _space{};
    };
} // namespace etask::comm::protocol

#include "packet_header.inl"

#endif // PROTOCOL_PACKET_HEADER_HPP_