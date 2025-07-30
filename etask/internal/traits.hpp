/**
* @file traits.hpp
*
* @brief Provides custom type traits for template metaprogramming.
*
* @ingroup etask_internal etask::internal
*
* This file defines additional type traits outside of the C++ standard library.
* These traits are designed for use in modern template metaprogramming,
* following the same structure and naming conventions as standard library traits.
* 
* @note These traits reside in the `etask::internal` namespace to avoid collision
* with standard traits and other libraries.
* 
* @warning This file is intended to use on platforms supporting C++17 standard or later.
*
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
#ifndef ETASK_INTERNAL_TRAITS_HPP_
#define ETASK_INTERNAL_TRAITS_HPP_
#include <type_traits> // For std::true_type, std::bool_constant, std::is_same_v
#include <limits> // For std::numeric_limits
#include <cstdint> // For std::uint8_t, std::uint16_t, std::uint32_t, std::uint64_t
namespace etask::internal {
    
    /**
    * @struct is_distinct
    * @brief Checks whether a pack of types is composed of distinct types.
    *
    * This type trait determines at compile-time whether all types provided in the parameter pack
    * are unique (i.e., no duplicates). The check is performed recursively using fold expressions
    * and `std::is_same_v`.
    *
    * The result is accessible via the `::value` member or via the `is_distinct_v` alias.
    *
    * @tparam Ts The parameter pack of types to check for uniqueness.
    *
    * @note This trait is useful when implementing compile-time type sets or constraints where
    * repeated types would cause ambiguity or incorrect behavior.
    *
    * @see is_distinct_v
    */
    template <typename...>
    struct is_distinct : std::true_type {};
    
    /**
    * @brief Recursive specialization of `is_distinct` to check for duplicate types.
    *
    * Evaluates whether the current type `T` is not the same as any of the remaining types,
    * and then recursively checks the rest.
    *
    * @tparam T The first type to compare.
    * @tparam Rest The remaining types in the parameter pack.
    */
    template <typename T, typename... Rest>
    struct is_distinct<T, Rest...> : std::bool_constant<
    (!std::is_same_v<T, Rest> && ...) && is_distinct<Rest...>::value
    > {};
    
    /**
    * @var is_distinct_v
    * @brief Convenience variable template for `is_distinct<Ts...>::value`.
    *
    * Evaluates to `true` if all types in the pack `Ts...` are distinct, `false` otherwise.
    *
    * @tparam Ts The types to check for uniqueness.
    *
    * @see is_distinct
    */
    template <typename... Ts>
    inline constexpr bool is_distinct_v = is_distinct<Ts...>::value;
    
    
    /**
    * @brief Helper function to retrieve the underlying value of an enum.
    * 
    * This function template takes an enum value and returns its underlying type.
    * 
    * @tparam T an `enum class` type.
    * 
    * @param v the enum value to convert.
    * 
    */
    template<typename T>
    constexpr std::underlying_type_t<T> underlying_v(T v){
        return static_cast<std::underlying_type_t<T>>(v);
    }
    
    /**
    * @var always_false_v
    * @brief Template-dependent compile-time false value for triggering conditional static_assert.
    *
    * This utility is used in `if constexpr` or other SFINAE-based contexts to intentionally
    * trigger a `static_assert` only when a specific template branch is instantiated.
    * 
    * Unlike `false` or `std::false_type::value`, this variable is *dependent* on the template
    * parameter `T`, ensuring that the compiler will only evaluate it when that branch is chosen.
    * 
    * This is particularly useful in generic functions or traits where a catch-all `else` branch
    * should cause a compile-time error only if it is actually reached.
    *
    * @tparam T A template type used to make the expression type-dependent.
    *
    * @code
    * template <typename T>
    * void process(const T&) {
    *     if constexpr (std::is_integral_v<T>) {
    *         // Handle integers
    *     } else {
    *         static_assert(always_false_v<T>, "Unsupported type in process()");
    *     }
    * }
    * @endcode
    *
    * @note This is a common metaprogramming idiom adopted by many modern C++ codebases.
    */
    template <typename T>
    constexpr bool always_false_v = false;
    
    
    /**
    * @brief Provides a member typedef `type` that names `T`.
    *
    * This struct performs the identity transformation on a type `T`, effectively
    * returning the same type. It's particularly useful in template metaprogramming
    * to prevent type deduction in certain contexts.
    *
    * @tparam T The type to be encapsulated.
    */
    template <class T>
    struct type_identity {
        using type = T; /**< The encapsulated type. */
    };
    
    /**
    * @brief Helper alias template for `type_identity`.
    *
    * Provides a convenient way to access the encapsulated type without explicitly
    * specifying `::type`.
    *
    * @tparam T The type to be encapsulated.
    */
    template <class T>
    using type_identity_t = typename type_identity<T>::type;
    
    
    // /**
    // * @struct template_parameter_of
    // *
    // * @brief Extracts the inner type of one or more template instantiations,
    // *        verifying that all inner types are the same.
    // *
    // * This struct extracts the type parameter of any template class that takes
    // * a single type argument (e.g. `task<int>`). When passed multiple template
    // * instances, it performs a static check to ensure all inner types are identical.
    // * Compilation fails if any types differ.
    // *
    // * @tparam Ts... A variadic pack of template instantiations to examine.
    // *
    // * @note Only templates of the form `Template<T>` are supported.
    // * @note Use `template_parameter_of_t<Ts...>` for a convenient alias.
    // */
    // template<typename... Ts>
    // struct template_parameter_of;
    
    // /// @brief Specialization for multiple template instantiations.
    // /// @tparam Arg the inner type of the first template instantiation.
    // /// @tparam ...Rest the remaining template instantiations to check.
    // template<
    // template<typename> class Outer,
    // typename Arg,
    // typename... Rest
    // >
    // struct template_parameter_of<Outer<Arg>, Rest...>
    // {
    //     // static check that all other Ts have same inner type Arg
    //     static_assert(
    //         (std::is_same_v<typename template_parameter_of<Rest>::type, Arg> && ...),
    //         "template_parameter_of error: not all inner types are the same."
    //     );
    
    //     using type = Arg;
    // };
    
    // ///@brief Specialization for a single template instantiation.
    // ///@tparam Outer the template class.
    // ///@tparam Arg the inner type of the template instantiation.
    // template<
    // template<typename> class Outer,
    // typename Arg
    // >
    // struct template_parameter_of<Outer<Arg>>
    // {
    //     using type = Arg;
    // };
    
    // /// @brief Convenience alias for `template_parameter_of<Ts...>::type`.
    // /// @tparam Ts... A variadic pack of template instantiations.
    // /// 
    // /// This alias allows easy access to the extracted type without needing to
    // /// explicitly refer to `template_parameter_of<Ts...>::type`.
    // /// 
    // /// @note If the pack contains multiple template instantiations, it will
    // ///       perform a static check to ensure all inner types are the same.
    // template<typename... Ts>
    // using template_parameter_of_t = typename template_parameter_of<Ts...>::type;
    
    
    
    /**
    * @struct member
    *
    * @brief Extracts and validates the common type of a static member across multiple types.
    *
    * The `member` metafunction recursively:
    *
    * - invokes a user-supplied extractor metafunction on each type
    * - extracts the declared type of the static member
    * - verifies that all extracted types are identical
    *
    * Compilation fails if any types differ.
    *
    * @tparam Extractor
    *         A template metafunction of the form:
    *         @code
    *         template<typename T>
    *         struct Extractor {
    *             static constexpr auto value = T::member_name;
    *         };
    *         @endcode
    *   
    *
    * @tparam First
    *         The first type from which to extract the member value.
    *
    * @tparam Rest
    *         Zero or more additional types to check for type consistency.
    *
    * @note Only extracts the type of the static constant member, not its value.
    *
    * @note For convenient use, prefer the alias template `member_t`.
    */
    template<template<typename> class Extractor, typename First, typename... Rest>
    struct member
    {
        /**
        * @brief The common type extracted from the static member of all types.
        *
        * This alias resolves to the deduced type from:
        * @code
        * decltype(Extractor<T>::value)
        * @endcode
        * for each type `T` in the parameter pack.
        *
        * A static assertion guarantees that all types yield the same result.
        */
        using type = typename member<Extractor, First>::type;
        
        static_assert(
            (std::is_same_v<type, std::remove_cv_t<decltype(Extractor<Rest>::value)>> && ...),
            "member error: not all Extractor<Ts> yield the same type."
        );
    };
    
    /**
    * @struct member (single-type specialization)
    *
    * @brief Specialization of `member` for a single type.
    *
    * Provides the extracted member type from a single type via the supplied extractor.
    *
    * @tparam Extractor
    *         The extractor metafunction used to retrieve the static member.
    *
    * @tparam T
    *         The type whose static member is extracted.
    */
    template<template<typename> class Extractor, typename T>
    struct member<Extractor, T>
    {
        /// @brief The extracted type of the static member for the given type.
        using type = std::remove_cv_t<decltype(Extractor<T>::value)>;
    };
    
    /**
    * @brief Alias template for easier use of `member`.
    *
    * Simplifies extraction of the common member type across multiple types:
    *
    * Example usage:
    * ```
    * template<typename T>
    * struct Extractor {
    *     static constexpr auto value = T::member_name;
    * };
    * 
    * using member_type = member_t<Extractor, A, B, C>;
    * ```
    *
    * @tparam Extractor
    *         The extractor metafunction used to retrieve the static member.
    *
    * @tparam Ts...
    *         The types whose static members should be extracted and checked.
    *
    * @see member
    */
    template<template<typename> class Extractor, typename... Ts>
    using member_t = typename member<Extractor, Ts...>::type;
    
    
    /**
    * @brief Retrieves the N-th type from a parameter pack.
    *
    * Primary template to index into a typelist-like parameter pack.
    *
    * @tparam N Zero-based index.
    * @tparam T First type in the list.
    * @tparam Ts Remaining types in the list.
    */
    template<size_t N, typename T, typename...Ts>
    struct nth{
        static_assert(N < sizeof...(Ts) + 1, "Index out of bounds");
        using type = std::conditional_t<N == 0, T, typename nth<N - 1, Ts...>::type>;
    };
    
    /**
    * @brief Specialization for the base case of N=0.
    *
    * Returns the first type in the list.
    */
    template<typename T, typename... Ts>
    struct nth<0, T, Ts...> {
        using type = T;
    };
    
    
    /**
    * @brief Type trait that resolves to the smallest unsigned integer type
    *        capable of holding a given constant value.
    *
    * This trait selects the smallest type among std::uint8_t, std::uint16_t,
    * std::uint32_t, and std::uint64_t that can represent the given value `V`.
    *
    * @tparam V The constant unsigned value to evaluate.
    *
    * @note This trait fails to compile if V exceeds the range of std::uint64_t.
    *
    * @example
    * ```
    * smallest_uint_t<100>       // resolves to std::uint8_t
    * smallest_uint_t<70000>     // resolves to std::uint32_t
    * ```
    */
    template <std::uintmax_t V>
    using smallest_uint_t =
        std::conditional_t<(V <= std::numeric_limits<std::uint8_t>::max()),  std::uint8_t,
            std::conditional_t<(V <= std::numeric_limits<std::uint16_t>::max()), std::uint16_t,
                std::conditional_t<(V <= std::numeric_limits<std::uint32_t>::max()), std::uint32_t,
                    std::conditional_t<(V <= std::numeric_limits<std::uint64_t>::max()), std::uint64_t,
                        void
                    >
                >
            >
        >;
    
} // namespace etask::internal

#endif // ETASK_INTERNAL_TRAITS_HPP_
