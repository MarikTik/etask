// SPDX-License-Identifier: BSL-1.1
/**
* @file channels.hpp
*
* @brief Aggregated header for all user-defined channel implementations.
*
* This file includes both `external_channel.hpp` and `internal_channel.hpp`
* so that user applications can import all available channel types with a
* single include. It is intended to be the primary entry point for channel
* definitions in user projects.
*
* @note This file is user-owned. Add or remove includes here to reflect
*       the set of channels available in your application.
*
* @author Mark Tikhonov
*
* @date 2025-08-10
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef CHANNELS_CHANNELS_HPP_
#define CHANNELS_CHANNELS_HPP_
#include "external_channel.hpp"
#include "internal_channel.hpp"
#endif //CHANNELS_CHANNELS_HPP_