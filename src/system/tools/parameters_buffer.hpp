/**
* @file parameters_buffer.hpp
* @brief Defines the `parameters_buffer` class for storing and extracting task parameters.
*
* This file defines the `parameters_buffer` class, which manages a fixed-size buffer
* of bytes used to store and extract parameters for tasks. It provides
* constructors to initialize the data from arrays and a method to extract
* parameters into typed values using a deserializer.
*/
#ifndef SYSTEM_TOOLS_PARAMETERS_BUFFER_HPP_
#define SYSTEM_TOOLS_PARAMETERS_BUFFER_HPP_
#include <cstddef>
#include <tuple>

namespace etask::system::tools {
    /**
    * @class parameters_buffer
    * @brief Encapsulates raw parameter storage and typed extraction for task execution.
    *
    * The `parameters_buffer` class holds a byte buffer and tracks the amount of data stored.
    * It allows constructing parameter sets from byte arrays, and later extracting
    * those parameters as a tuple of specified types.
    *
    * Designed for embedded contexts, it avoids dynamic memory allocation and ensures
    * fixed-size storage. It deletes move operations for clarity of ownership.
    *
    * @tparam Capacity The total size, in bytes, of the internal parameter buffer.
    */
    template<std::size_t Capacity>
    class parameters_buffer {
        static_assert(Capacity > 0, "parameters_buffer size must be greater than zero.");
    public:
        /**
        * @brief Constructs parameters_buffer from a compile-time sized byte array.
        *
        * Copies data from the provided array into the internal buffer.
        * Ensures that the data fits within the parameter capacity.
        *
        * @tparam N Size of the input data array.
        * @param data The byte array to initialize the parameters_buffer with.
        *
        * @throw assertion error if N exceeds Capacity (enforced via static_assert).
        */
        template<std::size_t N>
        inline parameters_buffer(const std::byte (&data)[N]);
        
        /**
        * @brief Copy constructor.
        *
        * Creates a new `parameters_buffer` object as a deep copy of another.
        *
        * @param other The object to copy.
        */
        inline parameters_buffer(const parameters_buffer& other);
        
        /**
        * @brief Copy assignment operator.
        *
        * Replaces the contents of this object with a deep copy of another.
        *
        * @param other The object to copy.
        * @return Reference to this object.
        */
        inline parameters_buffer& operator=(const parameters_buffer& other);
        
        /**
        * @brief Extracts stored parameters_buffer as a tuple of specified types.
        *
        * Uses a deserializer to convert the internal byte data into
        * a tuple of types provided via template arguments.
        *
        * @tparam T... Types to extract from the parameter data.
        * @return A tuple of extracted parameters.
        *
        * @throw assertion error if the combined size of types exceeds the capacity (enforced via static_assert).
        */
        template<typename... T>
        inline std::tuple<T...> extract() const;
        
        /**
        * @brief Returns the fixed capacity of the internal buffer.
        *
        * @return The total capacity of the parameters_buffer buffer in bytes.
        */
        static constexpr std::size_t capacity();
        
        /**
        * @brief Returns the current size of stored data.
        *
        * @return The number of bytes currently stored in the parameters_buffer.
        */
        inline std::size_t size() const;
        
        /// Deleted move constructor to enforce deep copy semantics.
        parameters_buffer(parameters_buffer&& other) noexcept = delete;
        
        /// Deleted move assignment operator to enforce deep copy semantics.
        parameters_buffer& operator=(parameters_buffer&& other) noexcept = delete;
        
    private:
        std::byte _data[Capacity]{}; ///< Internal byte buffer for parameter storage.
        std::size_t _size{};         ///< Number of bytes currently stored in the buffer.
    };
    
} // namespace etask::system::tools

#include "parameters_buffer.tpp"
#endif // SYSTEM_TOOLS_parameters_buffer_HPP_
