#ifndef SYSTEM_TOOLS_PARAMETERS_BUFFER_TPP_
#define SYSTEM_TOOLS_PARAMETERS_BUFFER_TPP_
#include "parameters_buffer.hpp"
#include <cassert>
#include <cstring>
#include <binary/deserializer.hpp>

namespace etask::system::tools{
    template <size_t Capacity>
    template <size_t N>
    inline parameters_buffer<Capacity>::parameters_buffer(const std::byte (&data)[N])
        : _size{N}
    {
        static_assert(N <= Capacity, "Data size exceeds parameters_buffer capacity.");
        std::memcpy(_data, data, N);
    }

    template<size_t Capacity>
    inline parameters_buffer<Capacity>::parameters_buffer(const parameters_buffer &other)
        : _size{other._size}
    {
        std::memcpy(this->_data, other._data, _size);
    }

    template<size_t Capacity>
    inline parameters_buffer<Capacity> &parameters_buffer<Capacity>::operator=(const parameters_buffer &other)
    {
        if (this != &other) {
            _size = other._size;
            std::memcpy(_data, other._data, _size);
        }
        return *this;
    }

    template <std::size_t Capacity>
    constexpr std::size_t parameters_buffer<Capacity>::capacity()
    {
        return Capacity;
    }

    template<size_t Capacity>
    inline std::size_t parameters_buffer<Capacity>::size() const
    {
        return _size;
    }

    template <size_t Capacity>
    template <typename... T>
    inline auto parameters_buffer<Capacity>::extract() const{
        static_assert(sizeof...(T) <= Capacity, "Total size of types (sum of sizeof...(T)) exceeds the size of buffer.");
        return ser::binary::deserialize(_data, Capacity).template to<T...>();
    }
} // namespace etask::system::tools

#endif // SYSTEM_TOOLS_PARAMETERS_BUFFER_TPP_