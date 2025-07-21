/**
* @file envelope_view.tpp
*
* @brief Implements `etask::tools::envelope_view` methods.
*
* This file provides template-based implementation details of the `envelope_view` class,
* including deserialization routines.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
* @date 2025-07-20
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef ETASK_TOOLS_ENVELOPE_VIEW_TPP_
#define ETASK_TOOLS_ENVELOPE_VIEW_TPP_
#include "envelope_view.hpp"
#include <ser/binary/deserializer.hpp>
namespace etask::tools {
    envelope_view::envelope_view(const std::byte *data, std::size_t size) noexcept
        : _data{data}, _size{size}
    {
    }

    const std::byte* envelope_view::data() const noexcept {
        return _data;
    }

    std::size_t envelope_view::size() const noexcept {
        return _size;
    }

     template<typename... Ts>
    inline std::tuple<Ts...> envelope_view::unpack() const {
        return ser::binary::deserialize(_data, _size).template to<Ts...>();
    }

} // namespace etask::tools

#endif // ETASK_TOOLS_ENVELOPE_VIEW_TPP_