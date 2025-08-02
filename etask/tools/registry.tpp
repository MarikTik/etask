/**
* @file registry.tpp
*
* @brief implementation of registry.hpp methods.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-07-29
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*
* @par Changelog
* - 2025-07-29
*      - Initial creation.
* - 2025-08-01
*      - Removed use of bitset to track constructed objects following update in `tools::slot`.
*/
#ifndef ETASK_TOOLS_REGISTRY_TPP_
#define ETASK_TOOLS_REGISTRY_TPP_
#include "registry.hpp"
#include <algorithm>

#define registry_template \
    template < \
        typename Base, \
        template<typename> typename Extractor, \
        typename... DerivedTypes, \
        typename... ConstructorArgs \
    >
#define registry_type \
    registry<  \
        Base, \
        Extractor, \
        internal::typelist<DerivedTypes...>, \
        internal::typelist<ConstructorArgs...> \
    >


namespace etask::tools {
    registry_template
    inline registry_type &registry_type::instance() noexcept {
        static registry_type instance; // Static instance for singleton pattern
        return instance;
    }
 
    
    registry_template
    inline Base* registry_type::get(key_t key) noexcept {
        auto it = std::lower_bound(_index_table.cbegin(), _index_table.cend(), key,
            [](const auto &entry, const auto &value){
                return entry.key < value;
            }
        );

        if (
            it == _index_table.cend()  or
            it->key not_eq key
        ) return nullptr; 

        return _routing_table[it->index].getter();
    }

    registry_template
    inline Base* registry_type::construct(key_t key, ConstructorArgs &&...args) noexcept
    {
        auto it = std::lower_bound(_index_table.cbegin(), _index_table.cend(), key,
            [](const auto &entry, const auto &value){
                return entry.key < value;
            }
        );
 
        if (
            it == _index_table.cend() or
            it->key not_eq key
        ) return nullptr;

        return _routing_table[it->index].constructor(std::forward<ConstructorArgs>(args)...);
    }

    registry_template
    inline void registry_type::destroy(key_t key) noexcept {
        auto it = std::lower_bound(_index_table.cbegin(), _index_table.cend(), key,
            [](const auto &entry, const auto &value){
                return entry.key < value;
            }
        );

        if (
            it == _index_table.cend() or
            it->key not_eq key
        ) return; 

        _routing_table[it->index].destructor();
    }

    registry_template
    registry_type::registry() noexcept{
        std::sort(_index_table.begin(), _index_table.end(), [](const auto& a, const auto& b) {
            return a.key < b.key;
        });
    }

    registry_template
    registry_type::~registry() {
        for (std::size_t i = 0; i < _index_table.size(); ++i) {
            const auto& slot = _index_table[i]; 
            _routing_table[slot.index].destructor();
        }
    }

    registry_template
    constexpr typename registry_type::routing_table_t registry_type::make_routing_table() const {
        return {{
            {
                []() noexcept -> Base* { 
                    return slot<DerivedTypes>::instance().get(); 
                },
                [](ConstructorArgs&&... args) noexcept -> Base* { 
                    return slot<DerivedTypes>::instance().construct(std::forward<ConstructorArgs>(args)...); 
                },
                []() noexcept -> void { 
                    slot<DerivedTypes>::instance().destroy(); 
                }
            }...
        }};
    }

    registry_template
    template <std::size_t... Is>
    constexpr typename registry_type::index_table_t registry_type::make_index_table_impl(std::index_sequence<Is...>) const {
        return {{
            mapping{Extractor<DerivedTypes>::value, static_cast<index_t>(Is)}...
        }};
    }
    
    registry_template
    constexpr typename registry_type::index_table_t registry_type::make_index_table() const{
        return make_index_table_impl(std::index_sequence_for<DerivedTypes...>{});
    }
}

#endif // ETASK_TOOLS_REGISTRY_TPP_