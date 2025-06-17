#ifndef PROTOCOL_VALIDATOR_TPP_
#define PROTOCOL_VALIDATOR_TPP_
#include "validator.hpp"
#include "compute.hpp"
namespace etask::comm::protocol {

    template <std::size_t PacketSize, typename TaskID_UnderlyingType>
    inline bool validator<basic_packet<PacketSize, TaskID_UnderlyingType>>::is_valid(const packet_t &packet) const
    {
        return true; // Basic packet validation always returns true, as it has no checksum
    }
    template <std::size_t PacketSize, typename TaskID_UnderlyingType>
    inline void validator<basic_packet<PacketSize, TaskID_UnderlyingType>>::seal(packet_t &packet) const
    {
        // No sealing required for basic packets, as they do not have a checksum
        // This function is provided for interface consistency
    }


    template <std::size_t PacketSize, typename TaskID_UnderlyingType, typename ChecksumPolicy>
    inline void validator<framed_packet<PacketSize, TaskID_UnderlyingType, ChecksumPolicy>>::seal(packet_t &packet) const
    {
        // Compute the checksum for the header, task_id, and payload
        packet.fcs = compute<ChecksumPolicy>(
            reinterpret_cast<const std::byte*>(&packet),
            packet.packet_size - ChecksumPolicy::size
        );
    }

    template <std::size_t PacketSize, typename TaskID_UnderlyingType, typename ChecksumPolicy>
    inline bool validator<framed_packet<PacketSize, TaskID_UnderlyingType, ChecksumPolicy>>::is_valid(const packet_t &packet) const
    {
        // Compute the expected checksum for the header, task_id, and payload and compare with the stored fcs
        return packet.fcs == compute<ChecksumPolicy>(
            reinterpret_cast<const std::byte*>(&packet),
            packet.packet_size - ChecksumPolicy::size
        );
    }
} // namespace etask::comm::protocol

#endif // PROTOCOL_VALIDATOR_TPP_