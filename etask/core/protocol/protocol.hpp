// SPDX-License-Identifier: MIT
/**
* @file protocol.hpp
*
* @brief Aggregates the etask application-layer wire protocol.
*
* @ingroup etask_core etask::core::protocol
*
* Mirrors `ecomm::protocol` one layer up: `ecomm::protocol` is the transport
* frame (`packet`/`packet_header`), `etask::core::protocol` is the application
* message riding inside that frame's opaque payload (`directive`, `request`,
* `reply`) - the schema `ecomm::packet` deliberately leaves undefined.
*
* `preamble` and `handshake` are the deliberate exception: they sit *beside* the
* frame rather than inside it, because their job is to establish that both peers
* build the same frame in the first place. See preamble.hpp for why that one
* message cannot itself be a packet.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-07-13
*
* @copyright
* MIT License
* Copyright (c) 2026 Mark Tikhonov
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_PROTOCOL_PROTOCOL_HPP_
#define ETASK_CORE_PROTOCOL_PROTOCOL_HPP_
#include "directive.hpp"
#include "request.hpp"
#include "reply.hpp"
#include "preamble.hpp"
#include "handshake.hpp"
#endif // ETASK_CORE_PROTOCOL_PROTOCOL_HPP_
