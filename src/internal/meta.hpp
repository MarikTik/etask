/**
* @file meta.hpp
*
* @brief Provides advanced metaprogramming utilities for the etask framework.
*
* @ingroup etask_internal etask::internal
*
* This header provides internal utilities for advanced C++ metaprogramming within the etask framework.
* It focuses not on classical type traits, but on **meta-constructs** that map compile-time information
* into runtime objects or facilitate generic code creation.
*
* ## Features
*
* - Safe object construction using custom allocators
* - Compile-time generation of lookup tables mapping values to factory functions
*
* ### Example: Mapping UID Values to Object Constructors
*
* One of the key tools in this file is `make_table`, which builds a **runtime lookup table**
* that maps compile-time constants (like unique IDs) to factory functions for creating objects
* derived from a common base type.
*
* @code{.cpp}
* #include <iostream>
* #include <memory>
* #include <array>
* #include <type_traits>
*
* struct Base {
*     virtual void hello() const = 0;
*     virtual ~Base() = default;
* };
*
* struct Foo : Base {
*     static constexpr int uid = 42;
*     void hello() const override { std::cout << "I am Foo\n"; }
* };
*
* struct Bar : Base {
*     static constexpr int uid = 17;
*     void hello() const override { std::cout << "I am Bar\n"; }
* };
*
* template <typename T>
* struct get_uid {
*     static constexpr int value = T::uid;
* };
*
* auto table = etask::internal::make_table<
*     Base,                    // Base type
*     get_uid,                 // Metafunction to extract uid
*     std::allocator<void>,    // Allocator type (defaulted)
*     Foo, Bar                 // Types to register
* >();
*
* int uid_to_find = 42;
*
* // Assuming the table is sorted by uid values, we can use binary search
* // otherwise linear search would suffice
*
* auto it = std::lower_bound(
*     table.cbegin(),
*     table.cend(),
*     uid_to_find,
*     [](const auto& entry, int val) {
*         return entry.value < val;
*     });
*
* if (it != table.cend() && it->value == uid_to_find) {
*     std::allocator<void> alloc;
*     Base* obj = it->constructor(alloc);
*     obj->hello();
*     delete obj;
* }
* else {
*     std::cout << "Not found\n";
* }
* @endcode
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2025-07-08
*
* @copyright
* Business Source License 1.1 (BSL 1.1)
* Copyright (c) 2025 Mark Tikhonov
* Free for non-commercial use. Commercial use requires a separate license.
* See LICENSE file for details.
*/
#ifndef ETASK_INTERNAL_META_HPP_
#define ETASK_INTERNAL_META_HPP_
#include "typelist.hpp"
#include <array>
#include <memory>
#include <type_traits>

namespace etask::internal {
    namespace __details{
        /**
        * @brief Constructs an instance of a derived type using a custom allocator.
        *
        * @tparam BaseType     The polymorphic base class type.
        * @tparam DerivedType  The concrete type to construct, must inherit from BaseType.
        * @tparam Allocator    An allocator type suitable for allocating DerivedType.
        *
        * @param alloc An allocator instance used for object allocation and construction.
        *
        * @return Pointer to a newly constructed DerivedType object, returned as BaseType*.
        *
        * @note
        * - Ensures type safety via static assertions.
        * - Rebinds the allocator automatically for the derived type.
        */
        template <typename BaseType, typename DerivedType, typename Allocator>
        BaseType* construct(const Allocator& alloc = Allocator{})
        {
            static_assert(std::is_base_of_v<BaseType, DerivedType>, "DerivedType must inherit from BaseType");
            static_assert(std::is_base_of_v<Allocator, std::allocator<DerivedType>>, "Allocator must be a specialization of std::allocator for DerivedType");
            
            using rebound_alloc = typename std::allocator_traits<Allocator>::template rebind_alloc<DerivedType>;
            rebound_alloc reb_alloc(alloc);
            DerivedType* p = reb_alloc.allocate(1);
            std::allocator_traits<rebound_alloc>::construct(reb_alloc, p);
            return p;
        }
    }
    
    /**
    * @brief Generates a compile-time lookup table mapping values to factory functions for creating derived objects.
    *
    * This metafunction constructs a table associating a unique value extracted from each derived type
    * with a factory function that can instantiate objects of that type via an allocator.
    *
    * This is useful for cases where you want to map **runtime values** back
    * to specific types at runtime and construct the appropriate polymorphic objects.
    *
    * @tparam BaseType
    *         The polymorphic base class type to which all derived types belong.
    *
    * @tparam MemberExtractor
    *         A template metafunction that extracts a unique identifying value from a given type.
    *         It must have the form:
    *         @code
    *         template<typename T>
    *         struct MemberExtractor {
    *             static constexpr auto value = ...;
    *         };
    *         @endcode
    *
    * @tparam Allocator
    *         The allocator type to use for constructing derived objects.
    *         Defaults to std::allocator<BaseType>. This allocator will be rebound
    *         internally to each derived type to support proper memory allocation.
    *
    * @tparam First
    *         The first derived type to register in the lookup table.
    *
    * @tparam Rest
    *         Zero or more additional derived types to register.
    *
    * @return
    *         An std::array of entries. Each entry consists of:
    *         - `value`: the unique value extracted from the type via MemberExtractor
    *         - `constructor`: a function pointer taking an allocator and returning a BaseType* pointing to a newly constructed derived object.
    *
    * @note
    * - This implementation uses a static_assert to ensure all derived types yield the same value type
    *   when passed through MemberExtractor.
    * - The resulting table is suitable for runtime binary search.
    * - Requires at least one type to be specified.
    */
    template <
    typename BaseType, 
    template<typename> typename MemberExtractor,
    typename Allocator = std::allocator<BaseType>,
    typename First,
    typename... Rest
    >
    constexpr auto make_table()
    {
        static_assert(sizeof...(Rest) > 0, "At least one type must be provided");
        
        using value_type = decltype(MemberExtractor<First>::value);
        
        static_assert((std::is_same_v<value_type, decltype(MemberExtractor<Rest>::value)> && ...), "All MemberExtractor::value types must be identical.");
        
        struct entry {
            value_type value;
            BaseType* (*constructor)(const Allocator&);
        };   
        
        return std::array<entry, 1 + sizeof...(Rest)> {{
            entry{ 
                MemberExtractor<First>::value,
                [](const Allocator& alloc) -> BaseType* { return __details::construct<BaseType, First, Allocator>(alloc);}
            },
            entry{ 
                MemberExtractor<Rest>::value,
                [](const Allocator& alloc) -> BaseType* { return __details::construct<BaseType, Rest, Allocator>(alloc); }
            }...
        }};
    }

} // namespace etask::internal

#endif // ETASK_INTERNAL_META_HPP_