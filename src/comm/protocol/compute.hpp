/**
* @file compute.hpp
*
* @brief Checksum computation engines for etask::comm protocol framework.
*
* @ingroup etask_comm_protocol etask::comm::protocol
* 
* This file declares the platform-independent checksum metafunctions 
* responsible for computing various checksum algorithms.
* 
* The implementations may later be specialized for specific embedded platforms
* (ESP32, ARM Cortex, etc) to leverage hardware acceleration where available.
* Otherwise, portable reference implementations will be provided.
* 
* @note These algorithms assume fixed endianness behavior defined by the protocol.
* @note Payload alignment or packing issues must be handled by caller.
* 
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-07-03
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef ETASK_COMM_PROTOCOL_COMPUTE_HPP_
#define ETASK_COMM_PROTOCOL_COMPUTE_HPP_
#include <cstdint>
#include "checksum.hpp"

namespace etask::comm::protocol {
    /**
    * @struct compute
    * @brief Primary template (unspecialized) — intentionally undefined.
    * 
    * The compute struct template must be explicitly specialized for each supported 
    * checksum policy defined in `checksum.hpp`. It exposes a single `operator()` 
    * function that computes the checksum for the given data buffer.
    * 
    * @tparam ChecksumPolicy The checksum policy type (crc32, sum8, fletcher16, etc).
    */
    template<typename ChecksumPolicy> 
    struct compute;
    
    /**
    * @struct compute<sum8>
    * @brief Computes sum8 checksum for the given data.
    */
    template<>
    struct compute<sum8> {
        inline sum8::value_type operator()(const std::byte* data, size_t size) const;
    };
    
    /**
    * @struct compute<sum16>
    * @brief Computes sum16 checksum for the given data.
    */
    template<>
    struct compute<sum16> {
        inline sum16::value_type operator()(const std::byte* data, size_t size) const;
    };
    
    /**
    * @struct compute<sum32>
    * @brief Computes sum32 checksum for the given data.
    */
    template<>
    struct compute<sum32> {
        inline sum32::value_type operator()(const std::byte* data, size_t size) const;
    };
    
    /**
    * @struct compute<crc8>
    * @brief Computes crc8 checksum for the given data.
    */
    template<>
    struct compute<crc8> {
        inline crc8::value_type operator()(const std::byte* data, size_t size) const;
    };
    
    /**
    * @struct compute<crc16>
    * @brief Computes crc16 checksum for the given data.
    */
    template<>
    struct compute<crc16> {
        inline crc16::value_type operator()(const std::byte* data, size_t size) const;
    };
    
    /**
    * @struct compute<crc32>
    * @brief Computes crc32 checksum for the given data.
    */
    template<>
    struct compute<crc32> {
        inline crc32::value_type operator()(const std::byte* data, size_t size) const;
    };
    
    /**
    * @struct compute<crc64>
    * @brief Computes crc64 checksum for the given data.
    */
    template<>
    struct compute<crc64> {
        inline crc64::value_type operator()(const std::byte* data, size_t size) const;
    };

    /**
    * @struct compute<fletcher16>
    * @brief Computes fletcher16 checksum for the given data.
    */
    template<>
    struct compute<fletcher16> {
        inline fletcher16::value_type operator()(const std::byte* data, size_t size) const;
    };
    
    /**
    * @struct compute<fletcher32>
    * @brief Computes fletcher32 checksum for the given data.
    */
    template<>
    struct compute<fletcher32> {
        inline fletcher32::value_type operator()(const std::byte* data, size_t size) const;
    };
    
    /**
    * @struct compute<adler32>
    * @brief Computes adler32 checksum for the given data.
    */
    template<>
    struct compute<adler32> {
        inline adler32::value_type operator()(const std::byte* data, size_t size) const;
    };
    
    /**
    * @struct compute<internet16>
    * @brief Computes internet16 (one's complement sum) checksum.
    */
    template<>
    struct compute<internet16> {
        inline internet16::value_type operator()(const std::byte* data, size_t size) const;
    };
    
} // namespace etask::comm::protocol

#include "compute.tpp"
#endif // ETASK_COMM_PROTOCOL_COMPUTE_HPP_
