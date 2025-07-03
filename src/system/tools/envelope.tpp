#ifndef SYSTEM_TOOLS_ENVELOPE_TPP_
#define SYSTEM_TOOLS_ENVELOPE_TPP_
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
#endif // SYSTEM_TOOLS_ENVELOPE_TPP_