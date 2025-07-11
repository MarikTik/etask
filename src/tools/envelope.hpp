/**
* @file envelope.hpp
*
* @brief Defines the `envelope` class for managing task parameters and results in the etask framework.
*
* @ingroup etask_tools etask::tools
*
* The `envelope` class encapsulates a contiguous block of memory used for transmitting
* serialized data between tasks and the communication layer. It provides both ownership
* semantics for dynamically allocated data and convenient methods for packing and unpacking
* structured parameters or results.
*
* It replaces the need for separate parameters/result buffer classes by serving
* as a unified data carrier that supports both reading (unpacking) and writing (packing) operations.
*
* @note This class is move-only due to unique ownership of its memory block.
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
#ifndef ETASK_TOOLS_ENVELOPE_HPP_
#define ETASK_TOOLS_ENVELOPE_HPP_
#include <memory>
#include <cstddef>

namespace etask::tools{
    /**
    * @class envelope
    * @brief Owns and manages a block of memory used for transmitting serialized task parameters and results.
    *
    * The `envelope` class acts as a flexible data container for the etask communication protocol.
    * It provides:
    *
    * - ownership of a dynamically allocated memory block via unique_ptr
    * - methods for packing structured data into the block
    * - methods for unpacking data from the block into typed objects
    *
    * This class is designed to be returned from tasks (as results) or passed into tasks
    * as parameters, serving as the primary data exchange unit.
    *
    * @note The envelope is a move-only type and cannot be copied.
    */
    class envelope{
    public:
        
        /**
        * @brief Constructs an empty envelope.
        *
        * The internal memory pointer is null, and the size is zero.
        */
        inline envelope() noexcept = default;
        
        /**
        * @brief Constructs an envelope by taking ownership of the given memory block.
        *
        * @param data A unique_ptr to the allocated byte array containing the envelope contents.
        * @param size The size of the memory block in bytes.
        */
        inline envelope(std::unique_ptr<std::byte[]> data, std::size_t size);
        
        /**
        * @brief Move constructor.
        *
        * Transfers ownership of the memory block from another envelope.
        *
        * @param other The envelope to move from.
        */
        envelope(envelope&& other) noexcept = default;
        
        /**
        * @brief Move assignment operator.
        *
        * Transfers ownership of the memory block from another envelope.
        *
        * @param other The envelope to move from.
        * @return Reference to this object.
        */
        envelope& operator=(envelope&& other) noexcept = default;
        
        /**
        * @brief Unpacks the envelope contents into a tuple of typed values.
        *
        * Uses a deserialization mechanism to extract typed objects from
        * the underlying byte array.
        *
        * @tparam T... The types to deserialize and extract from the envelope.
        * @return A tuple containing the deserialized values.
        *
        * @note Throws if the deserialized size exceeds the envelope's size.
        */
        template<typename... T>
        inline std::tuple<T...> unpack() const;
        
        /**
        * @brief Packs one or more typed values into the envelope's memory block.
        *
        * This method serializes the given values into a dynamically allocated
        * memory block owned by the envelope.
        *
        * @tparam T... The types of the values to serialize.
        * @param args The values to serialize into the envelope.
        *
        * @note Any existing data in the envelope is discarded and replaced
        *       with the new packed contents.
        */
        template<typename... T>
        inline void pack(T&&... args);
        
        /**
        * @brief Returns a pointer to the internal byte data.
        *
        * Provides read-only access to the internal memory block.
        *
        * @return A const pointer to the byte data held by the envelope, or nullptr if empty.
        */
        inline const std::byte* data() const noexcept;
        
        /**
        * @brief Returns the size of the envelope's memory block in bytes.
        *
        * @return The number of bytes stored in the envelope.
        */
        inline std::size_t size() const;
        
        /// Delete copy constructor because envelope is a unique-ownership type.
        envelope(const envelope&) = delete;
        
        /// Delete copy assignment operator because envelope is a unique-ownership type.
        envelope& operator=(const envelope&) = delete;
    private:
        std::unique_ptr<std::byte[]> _data{};
        std::size_t _size{0};    
    };

} // namespace etask::tools

#include "envelope.tpp"
#endif // ETASK_TOOLS_ENVELOPE_HPP_