/**
* @file envelope.tpp
*
* @brief implementation of envelope.tpp methods.
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
#ifndef ETASK_SYSTEM_TOOLS_ENVELOPE_TPP_
#define ETASK_SYSTEM_TOOLS_ENVELOPE_TPP_
#include "envelope.hpp"
#include "traits.hpp"
#include "ser/binary/serializer.hpp"
#include "ser/binary/deserializer.hpp"

namespace etask::system::tools{
    
    envelope::envelope(std::unique_ptr<std::byte[]> data, std::size_t size):
        _data{std::move(data)},
        _size{size}
    {
    }

    inline const std::byte* envelope::data() const noexcept {
        return _data.get();
    }

    inline std::size_t envelope::size() const {
        return _size;
    }

    template<typename... T>
    inline std::tuple<T...> envelope::unpack() const {
        return ser::binary::deserialize(data(), _size).template to<T...>();
    }

    template<typename... T>
    inline void envelope::pack(T&&... args) {
        ser::binary::serialize(std::forward<T>(args)...).to(_data.get(), _size);
    }

} // namespace etask::system::tools

#endif // ETASK_SYSTEM_TOOLS_ENVELOPE_TPP_