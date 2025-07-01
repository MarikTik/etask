/**
* @file parameters_view.hpp
* @brief Declares the `parameters_view` class for non-owning views of task parameters.
*
* This file defines the `parameters_view` class, which provides a lightweight, non-owning
* view into a sequence of bytes representing serialized task parameters. It allows efficient
* inspection and deserialization of parameter data without taking ownership of the underlying memory.
*
* Typical use cases include:
* - viewing a memory region in a network packet
* - passing slices of memory to protocol layers
* - reading parameters from shared memory or buffers managed elsewhere
*
* The view is immutable and guarantees read-only access to the data it references.
*
* @note Unlike `parameters_buffer` (which owns and copies its data), `parameters_view` merely
* references existing memory and does not manage lifetimes. Users are responsible for ensuring
* the data remains valid for the lifetime of the view.
*
* @see parameters_buffer
*/

#ifndef SYSTEM_TOOLS_PARAMETERS_VIEW_HPP_
#define SYSTEM_TOOLS_PARAMETERS_VIEW_HPP_

#include <cstddef>
#include <tuple>

namespace etask::system::tools {
    /**
    * @class parameters_view
    * @brief Non-owning view of serialized task parameters.
    *
    * The `parameters_view` class provides a lightweight, non-owning view of a memory
    * region containing serialized task parameters. It exposes the data length and
    * supports deserialization into typed values via the `extract()` method.
    *
    * This class does not allocate memory or manage the lifetime of the underlying data.
    * It is intended for use cases where tasks process external or transient memory buffers.
    *
    * Example usage:
    * @code
    * const std::byte* raw_data = ...;
    * std::size_t length = ...;
    * parameters_view view{raw_data, length};
    *
    * auto [x, y] = view.extract<int, float>();
    * @endcode
    *
    * @note It is the caller's responsibility to ensure the lifetime of the data
    * referenced by this view exceeds the lifetime of the `parameters_view` instance.
    */
    class parameters_view {
    public:
        /**
        * @brief Constructs a parameters_view from a raw byte array.
        *
        * Initializes a view onto the specified memory region.
        * The view does not take ownership of the data and assumes
        * the memory remains valid for the lifetime of the view.
        *
        * @param data Pointer to the raw byte data.
        * @param size Size of the data in bytes.
        */
        inline parameters_view(const std::byte* data, std::size_t size);
        
        /**
        * @brief Deserializes the view’s bytes into a tuple of values.
        *
        * This method uses a deserializer to interpret the raw byte buffer
        * as a tuple of types specified by the caller. It is the caller’s
        * responsibility to ensure that the total size of the requested types
        * does not exceed the size of the view.
        *
        * @tparam T... The types to extract from the view.
        * @return A tuple containing the extracted values.
        *
        * @throws std::runtime_error or asserts if the data is too small
        *         for the requested types.
        *
        * @note This function assumes the byte ordering and alignment
        * requirements of the deserialized types are compatible with the
        * memory representation in the view.
        */
        template<typename... T>
        inline std::tuple<T...> extract() const;
        
        /**
        * @brief Returns the size of the view in bytes.
        *
        * This method reports how many bytes the view covers.
        * It does not reflect how many meaningful parameters may
        * be extracted without overflow—it merely reports the raw size.
        *
        * @return Number of bytes in the view.
        */
        inline std::size_t size() const;
        
        /**
        * @brief Returns a pointer to the raw data.
        *
        * Provides direct read-only access to the bytes referenced
        * by the view.
        *
        * @return Pointer to the start of the view’s data.
        */
        inline const std::byte* data() const noexcept;
        
    private:
        const std::byte* _data; ///< Pointer to the beginning of the parameter data.
        std::size_t _size;      ///< Size of the parameter data in bytes.
    };
} // namespace etask::system::tools

#include "parameters_view.tpp"
#endif // SYSTEM_TOOLS_PARAMETERS_VIEW_HPP_
