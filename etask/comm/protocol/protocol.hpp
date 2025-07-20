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
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-07-03
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
* @par Changelog
* - 2025-07-03 
*     - Initial creation.
* - 2025-07-15
*     - Added `ETASK_BOARD_ID` definition to ensure consistent board ID usage across the protocol if no user defined value is provided.
* - 2025-07-18
*     - Moved `ETASK_BOARD_ID` definition to `config.hpp` for better modularity and configuration management.
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