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
* One of the key tools in this file is `identity_table_gen`, which builds a **runtime lookup table**
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
* auto table = etask::internal::identity_table_gen<
*     Base,                    // Base type
*     get_uid,                 // Metafunction to extract uid
*     std::allocator<void>,    // Allocator type
*     etask::internal::typelist<Foo, Bar>,     // Types to register
*     etask::internal::typelist<>              // Constructor argument types
* >::value;
*
* int uid_to_find = 42;
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
* @date 2025-07-13
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
#include <utility>

namespace etask::internal {
    namespace __details{
        /**
        * @brief Constructs an instance of a derived type using a custom allocator.
        *
        * @tparam BaseType     The polymorphic base class type.
        * @tparam DerivedType  The concrete type to construct, must inherit from BaseType.
        * @tparam Allocator    An allocator type suitable for allocating DerivedType.
        * @tparam Args         Zero or more types that can be passed to the constructor of DerivedType.
        * @param alloc An allocator instance used for object allocation and construction.
        *
        * @return Pointer to a newly constructed DerivedType object, returned as BaseType*.
        *
        * @note
        * - Ensures type safety via static assertions.
        * - Rebinds the allocator automatically for the derived type.
        */
        template <typename BaseType, typename DerivedType, typename Allocator, typename... Args>
        BaseType* construct(const Allocator& alloc = Allocator{}, Args&&... args)
        {
            static_assert(std::is_base_of_v<BaseType, DerivedType>, "DerivedType must inherit from BaseType");
            
            using rebound_alloc = typename std::allocator_traits<Allocator>::template rebind_alloc<DerivedType>;
            rebound_alloc reb_alloc(alloc);
            DerivedType* p = reb_alloc.allocate(1);
            std::allocator_traits<rebound_alloc>::construct(reb_alloc, p, std::forward<Args>(args)...);
            return p;
        }
        
        /**
        * @brief Represents a single entry in the runtime lookup table mapping values to factory functions.
        *
        * Each entry stores:
        * - A compile-time unique value (e.g. UID or enum constant) associated with a specific derived type.
        * - A factory function pointer capable of constructing an instance of that derived type,
        *   returning it as a pointer to the base type.
        *
        * @tparam ValueType
        *         The type of the value extracted from the derived class (e.g. an integer UID or enum).
        *
        * @tparam BaseType
        *         The polymorphic base class type for all derived objects.
        *
        * @tparam Allocator
        *         The allocator type used to construct derived objects.
        *         This allocator will be rebound to the derived type as needed.
        *
        * @tparam Args
        *         Zero or more types forwarded as constructor arguments to the derived type.
        */
        template<typename ValueType, typename BaseType, typename Allocator, typename... Args>
        struct table_entry {
            ValueType value;
            BaseType* (*constructor)(const Allocator&, Args&&...);
        };
    }
    
    /**
    * @brief Generates a compile-time lookup table mapping unique values to factory functions for constructing derived objects.
    *
    * This metafunction constructs a table associating a unique value extracted from each derived type
    * with a factory function capable of instantiating objects of that type via an allocator.
    *
    * The resulting table is sorted by the extracted values to allow fast binary search at runtime.
    *
    * This is useful for cases where you want to map **runtime values** back
    * to specific types and dynamically construct the appropriate polymorphic objects.
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
    *         This allocator will be rebound internally to each derived type
    *         to support proper memory allocation.
    *
    * @tparam DerivedTypesList
    *         A `typelist` of all derived types to be registered in the lookup table.
    *         All types must be constructible using the provided constructor arguments.
    *
    * @tparam ConstructorArgsList
    *         A `typelist` of zero or more additional types passed to the constructors
    *         of the derived types. These arguments will be forwarded to the constructor
    *         of each derived type during instantiation.
    *
    * @return
    *         A static `std::array` of `table_entry` elements. Each entry contains:
    *         - `value`: the unique value extracted via `MemberExtractor`
    *         - `constructor`: a function pointer taking an allocator (and any additional arguments)
    *            and returning a pointer to a newly constructed derived object as `BaseType*`.
    *
    * @note
    * - This implementation uses a static_assert to ensure all derived types yield the same value type
    *   from the `MemberExtractor`.
    * - The table is automatically sorted in ascending order of extracted values,
    *   making it suitable for fast runtime binary search.
    * - Requires at least one derived type to be specified.
    */
    template<
    typename BaseType,
    template<typename> typename MemberExtractor,
    typename Allocator,
    typename DerivedTypesList,
    typename ConstructorArgsList
    >
    struct identity_table_gen;
    
    template<
    typename BaseType,
    template<typename> typename MemberExtractor,
    typename Allocator,
    typename First,
    typename... Rest,
    typename... Args
    >
    struct identity_table_gen<BaseType, MemberExtractor, Allocator, typelist<First, Rest...>, typelist<Args...>>
    {
        using value_type = std::remove_cv_t<decltype(MemberExtractor<First>::value)>;
        
        using entry = __details::table_entry<value_type, BaseType, Allocator, Args...>;
        
        template<typename T>
        static constexpr entry make_entry()
        {
            return entry{
                MemberExtractor<T>::value,
                [](const Allocator& alloc, Args&&... args) -> BaseType* {
                    return __details::construct<BaseType, T, Allocator>(alloc, std::forward<Args>(args)...);
                }
            };
        }
        
        static inline std::array<entry, 1 + sizeof...(Rest)> value = [](){
            auto arr = std::array<entry, 1 + sizeof...(Rest)> {
                make_entry<First>(),
                make_entry<Rest>()...
            };
            std::sort(arr.begin(), arr.end(), [](const entry& a, const entry& b) {
                return a.value < b.value;
            });
            return arr;
        }();
    };
} // namespace etask::internal

#endif // ETASK_INTERNAL_META_HPP_