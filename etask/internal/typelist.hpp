/**
* @file typelist.hpp
*
* @brief Defines a compile-time container for a parameter pack of types.
*
* @ingroup etask_internal etask::internal
*
* This header introduces the `etask::internal::typelist` struct — a utility
* that encapsulates a sequence of types at compile time. It is designed for use
* in template metaprogramming, compile-time dispatch, and type-based computation.
*
* Unlike `std::tuple`, this structure does not instantiate objects or store any
* data — it only carries type information and can be used for operations such as
* indexing, filtering, and expansion.
*
* @note This utility is conceptually similar to `type_list` in other metaprogramming libraries.
*
* ### Example usage:
* @code
* #include "typelist.hpp"
* using namespace etask::internal;
*
* // Define a typelist of some fundamental types
* using my_types = typelist<int, double, char>;
*
* // Example metafunction that computes the number of types
* template<typename List>
* struct typelist_size;
*
* template<typename... Ts>
* struct typelist_size<typelist<Ts...>> {
*     static constexpr std::size_t value = sizeof...(Ts);
* };
*
* static_assert(typelist_size<my_types>::value == 3, "Should contain 3 types");
* @endcode
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
#ifndef ETASK_INTERNAL_TYPELIST_HPP_
#define ETASK_INTERNAL_TYPELIST_HPP_

namespace etask::internal {
 
    /**
    * @struct typelist
    * @brief A container for a variadic list of types, used for compile-time type manipulation.
    *
    * The `typelist` struct stores types as a parameter pack without instantiating them.
    * It serves as a compile-time-only construct, useful for performing metaprogramming tasks
    * such as static dispatch, filtering, or trait extraction.
    *
    * @tparam Ts The types to store in the typelist.
    */
    template<typename... Ts>
    struct typelist {};

} // namespace etask::internal

#endif // ETASK_INTERNAL_TYPELIST_HPP_
 