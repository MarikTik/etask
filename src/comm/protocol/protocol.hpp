/**
* @file protocol.hpp
* @brief High-level communication protocol definitions for etask framework.
*
* This file aggregates all protocol components including packet headers, checksums,
* basic packet structures, and framed packets with checksum support.
* It provides a unified interface for constructing, parsing, and validating communication packets.
*
* The protocol is designed for efficient serialization, transmission, and integrity verification
* across potentially unreliable communication channels.
*
* The components are modular and can be extended or replaced as needed for specific use cases.
*
* The protocol supports:
* - Compact packet headers with metadata
* - Multiple checksum algorithms for integrity verification
* - Basic fixed-size packets for simple message passing
* - Framed packets with optional checksums for robust communication 
*/
#ifndef COMM_PROTOCOL_HPP_
#define COMM_PROTOCOL_HPP_
#include "packet_header.hpp"
#include "checksum.hpp"
#include "basic_packet.hpp"
#include "framed_packet.hpp"
#endif // COMM_PROTOCOL_HPP_