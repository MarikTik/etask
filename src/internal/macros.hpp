/**
* @file macros.hpp
*
* @brief Utility macros for compile-time introspection.
*
* @ingroup etask_internal etask::internal
*
* This header defines macros to facilitate compile-time checks for the existence
* of specific members within types. These utilities are particularly useful in
* template metaprogramming scenarios where behavior needs to adapt based on
* type traits.
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
#ifndef INTERNAL_MACROS_HPP_
#define INTERNAL_MACROS_HPP_
#include <type_traits>
#include <cstddef>
/**
* @brief Generates a type trait to detect the presence of a specific member variable in a class.
*
* This macro defines a template struct `has_member_<member>` that evaluates to `true` if
* the type `T` has a member variable named `<member>`, and `false` otherwise.
* It also defines a helper variable template `has_member_<member>_v`.
*
* @param member The name of the member variable to check for existence.
*
* @note The generated struct/variable can be used in compile-time checks (e.g., `if constexpr`, `static_assert`)
* to conditionally enable or disable code based on the presence of a member variable in a type.
*
* @warning This macro uses SFINAE based on taking the address of the member (`&T::member`).
* It may not correctly detect static members or members that cannot have their address taken.
* It generally requires the member to be accessible from the context where the trait is used.
*
* @example
* // Generate the trait for a member named 'id'
* create_has_member(id)
*
* struct MyStructWithId { int id; };
* struct MyStructWithoutId { double value; };
*
* static_assert(has_member_id_v<MyStructWithId>, "MyStructWithId should have member 'id'");
* static_assert(!has_member_id_v<MyStructWithoutId>, "MyStructWithoutId should not have member 'id'");
*/
#define create_has_member(member)                                                  \
template <typename T, typename = void>                                             \
struct has_member_##member : std::false_type {};                                   \
                                                                                   \
template <typename T>                                                              \
struct has_member_##member<T, std::void_t<decltype(&T::member)>>                   \
    : std::true_type {};                                                           \
                                                                                   \
template <typename T>                                                              \
inline constexpr bool has_member_##member##_v = has_member_##member<T>::value;     \
                                                                                   \

/**
* @brief Generates a type trait to detect the presence of a specific nested type alias or nested_type in a class.
*
* This macro defines a template struct `has_nested_type_<nested_type>` that evaluates to `true` if
* `typename T::<nested_type>` is a valid nested type name within class `T`, and `false` otherwise.
* It also defines a helper variable template `has_nested_type_<nested_type>_v`.
*
* @param nested_type The name of the nested type (e.g., alias created with `using` or `nested_type`) to check for existence.
*
* @note The generated struct/variable can be used in compile-time checks (e.g., `if constexpr`, `static_assert`)
* to conditionally enable or disable code based on the presence of a nested type definition in a class.
* This is useful for checking conventions or enabling specific template logic.
*
* @warning Requires C++17 for `std::void_t` (though often available in C++11/14 via library implementations).
* The nested type must be accessible from the context where the trait is used (typically public).
*
* @example
* // Generate the trait for a nested type named 'value_type'
* create_has_nested_type(value_type)
*
* struct Container { using value_type = int; };
* struct SimpleClass { double data; };
*
* static_assert(has_nested_type_value_type_v<Container>, "Container should have nested type 'value_type'");
* static_assert(!has_nested_type_value_type_v<SimpleClass>, "SimpleClass should not have nested type 'value_type'");
*
* // Example usage with your 'device_t' case:
* create_has_nested_type(device_t)
*
* class MyTask { public: using device_t = class MyDevice; };
* class AnotherTask { // something here };
*
* static_assert(has_nested_type_device_t_v<MyTask>, "MyTask should define device_t");
* static_assert(!has_nested_type_device_t_v<AnotherTask>, "AnotherTask should not define device_t");
*/
#define create_has_nested_type(nested_type)                                        \
template <typename T, typename = void>                                             \
struct has_nested_type_##nested_type : std::false_type {};                         \
                                                                                   \
template <typename T>                                                              \
struct has_nested_type_##nested_type<T, std::void_t<typename T::nested_type>>      \
    : std::true_type {};                                                           \
                                                                                   \
template <typename T>                                                              \
inline constexpr bool has_nested_type_##nested_type##_v =                          \
    has_nested_type_##nested_type<T>::value;      

#endif // INTERNAL_MACROS_HPP_