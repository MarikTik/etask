/**
* @file protocol.hpp
*
* @brief High-level communication protocol definitions for etask framework.
*
* @defgroup etask_comm_protocol etask::comm::protocol
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
#ifndef ETASK_COMM_PROTOCOL_HPP_
#define ETASK_COMM_PROTOCOL_HPP_
#include "packet_header.hpp"
#include "checksum.hpp"
#include "basic_packet.hpp"
#include "framed_packet.hpp"
#include "validator.hpp"
#include "compute.hpp"
#endif // ETASK_COMM_PROTOCOL_HPP_