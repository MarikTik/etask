/**
* @file config.hpp
*
* @brief Internal protocol configuration definitions for the etask communication framework.
*
* This header provides internal compile-time configuration options used by the protocol layer.
* Users are not expected to modify protocol metadata directly in code. Instead, static definitions
* like the unique board/device ID (`ETASK_BOARD_ID`) can be overridden via compiler flags or 
* global macro definitions.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-07-18
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef ETASK_COMM_PROTOCOL_CONFIG_HPP_
#define ETASK_COMM_PROTOCOL_CONFIG_HPP_
#ifndef ETASK_BOARD_ID
#define ETASK_BOARD_ID 0 ///< Default board/device ID (can be overridden externally)
#endif // ETASK_BOARD_ID
#endif // ETASK_COMM_PROTOCOL_CONFIG_HPP_