#ifndef SYSTEM_TOOLS_PARAMETERS_VIEW_TPP_
#define SYSTEM_TOOLS_PARAMETERS_VIEW_TPP_
#include "parameters_view.hpp"
#include <cassert>
#include <binary/deserializer.hpp>
namespace etask::system::tools {
    inline etask::system::tools::parameters_view::parameters_view(const std::byte *data, std::size_t size)
        : _data{data}, _size{size}
    {
    }

    template<typename... T>
    inline std::tuple<T...> parameters_view::extract() const {
        assert(_size >= sizeof...(T) && "Not enough data in parameters_view to extract the requested types.");
        return ser::binary::deserialize(reinterpret_cast<const uint8_t *>(_data), _size).template to<T...>();
    }

    inline const std::byte* etask::system::tools::parameters_view::data() const noexcept {
        return _data;
    }

    inline std::size_t etask::system::tools::parameters_view::size() const {
        return _size;
    }

} // namespace etask::system::tools
#endif // SYSTEM_TOOLS_PARAMETERS_VIEW_TPP_
