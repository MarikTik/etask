/**
* @file registry.hpp
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
*      - Updated documentation of private structures, methods and members.
*/
#ifndef ETASK_TOOLS_REGISTRY_HPP_
#define ETASK_TOOLS_REGISTRY_HPP_
#include "../internal/typelist.hpp"
#include "../internal/traits.hpp"
#include <bitset>
#include <array>
#include <algorithm>

namespace etask::tools {

    /**
    * @struct registry 
    * 
    * @brief A factory-style registry that maps keys to statically stored, lazily constructed objects.
    *
    * Each derived type is associated with a unique key via the Extractor metafunction.
    * Objects are constructed on demand and stored statically via `slot<T>`, enabling polymorphic access.
    *
    * @tparam Base The polymorphic base class of all derived types.
    * @tparam Extractor A metafunction returning a unique integral key for each derived type.
    * @tparam DerivedTypesList A typelist of all derived classes inheriting from Base.
    * @tparam ConstructorArgsList A typelist of constructor argument types required for all DerivedTypes.
    */
    template<
        typename Base,
        template<typename> typename Extractor,
        typename DerivedTypesList,
        typename ConstructorArgsList
    >
    class registry;

    /**
    * @brief Specialization of registry for unpacked DerivedTypes and ConstructorArgs.
    */
    template<
        typename Base,
        template<typename> typename Extractor,
        typename... DerivedTypes,
        typename... ConstructorArgs
    >
    class registry<
        Base,
        Extractor,
        internal::typelist<DerivedTypes...>,
        internal::typelist<ConstructorArgs...>
    > 
    {

        struct route; // Forward declaration for route struct
        struct mapping; // Forward declaration for mapping struct

        /**
        * @brief The number of derived types in this registry.
        * @note This is a compile-time constant deduced from the number of types in DerivedTypes.
        */
        static constexpr std::size_t capacity = sizeof...(DerivedTypes);

        /**
        * @typedef sample_t 
        * 
        * @brief The first derived type used to deduce key key type.
        */
        using sample_t = typename internal::nth<0, DerivedTypes...>::type;

        /**
        * @typedef key_t
        * 
        * @brief The type of the unique key for each derived type, deduced via Extractor metafunction.
        */
        using key_t = std::remove_cv_t<decltype(Extractor<sample_t>::value)>;

        /**
        * @typedef routing_table_t
        * 
        * @brief A type alias for the routing table, which is either a std::array or const std::array
        * depending on the number of derived types.
        * 
        * @note The intent of this conidtional type is to optimize memory usage for small numbers of derived types.
        * For most systems const arrays would be placed in RAM unless they are relatively large.
        * Larger numbers of derived types (> 256) will use const std::array with the intent to place it in ROM, 
        * saving RAM space with little to no performance impact.
        */
        using routing_table_t = internal::add_const_if_t<
            std::array<route, capacity>, 
            (capacity > std::numeric_limits<std::uint8_t>::max())
        >;

        /**
        * @typedef index_t
        * 
        * @brief The smallest unsigned integer type that can hold the index of a route in the registry.
        * This is used to redirect keys to routes by index.
        */
        using index_t = internal::smallest_uint_t<capacity>;

        /**
        * @typedef index_table_t
        * @brief A static array mapping keys to their corresponding indices in the routing table.
        * This allows for fast lookups of routes by key.
        * @note The array is sized to the capacity of the registry, ensuring it can hold all keys.
        */
        using index_table_t = std::array<mapping, capacity>;

        static_assert((std::is_nothrow_constructible_v<DerivedTypes, ConstructorArgs...> && ...), "All derived types must be nothrow constructible");
        static_assert((std::is_nothrow_destructible_v<DerivedTypes> && ...), "All derived types must be nothrow destructible");
    public: 
        static registry &instance() noexcept;
        /**
        * @brief Retrieves a pointer to the object associated with the given key, if constructed.
        * 
        * @param key The key associated with a derived type.
        * @return Base pointer if the object is constructed, or nullptr.
        */
        Base* get(key_t key) noexcept;

        /**
        * @brief Constructs the object associated with the given key.
        *
        * If already constructed, returns the existing instance.
        * 
        * @param key The key identifying a derived type.
        * @param args Arguments forwarded to the constructor.
        * @return Base pointer to the constructed object, or nullptr if the key is unknown.
        */
        Base* construct(key_t key, ConstructorArgs&&... args) noexcept;

        /**
        * @brief Destroys the object associated with the given key, if constructed.
        * 
        * @param key The key identifying the object to destroy.
        */
        void destroy(key_t key) noexcept;

        /**
        * @brief Destructor; destroys all constructed objects in reverse registry order.
        */
        ~registry();

        /// Delete copy constructor to prevent singleton misuse.
        registry(const registry&) = delete;

        /// Delete copy assignment operator to prevent singleton misuse.
        registry& operator=(const registry&) = delete;

        /// Delete move constructor to prevent singleton misuse.
        registry(registry&&) = delete;

        /// Delete move assignment operator to prevent singleton misuse.
        registry& operator=(registry&&) = delete;
    private:

        /**
        * @struct route
        * 
        * @brief A structure defining the routing table entry to control derived type access.
        * 
        * Contains function pointers for getting, constructing, and destoying the object.
        */
        struct route{
            Base* (*getter)() noexcept;  ///< Function returning a pointer to the instance.
            Base* (*constructor)(ConstructorArgs&&...) noexcept;  ///< Constructor function.
            void (*destructor)() noexcept;  ///< Destructor function.
        };

        /** 
        * @struct mapping
        * 
        * @brief A structure mapping a key to its index in the routing table.
        * 
        * This is used to quickly find the route for a given key
        * 
        * @note Internally the mappings are sorted by keys, so key search is O(log(n)) which is decent
        * for use cases of small to medium-sized registries, which is exactly what is intended, supposing
        * there will be no more than 2^16 entries in the `_routing_table` there is no memory impact in storing two 
        * table arrays (`_routing_table`, `_index_table`) vs one single table with the key being part of `route`.
        */
        struct mapping {
            key_t key;
            index_t index;
        };

        /**
        * @brief Constructs the registry and sorts internal mapping table by key.
        */
        registry() noexcept;

        /**
        * @brief Constructs a routing table with function pointers for each derived type.
        * 
        * This function initializes the routing table with getter, constructor, and destructor pointers
        * for each derived type.
        * 
        * @return A routing table with function pointers for each derived type.
        */
        constexpr routing_table_t make_routing_table() const;

        /**
        * @brief Constructs an index table mapping keys to their indices in the routing table.
        * 
        * This function creates an array that maps each key to its corresponding index in the routing table.
        * 
        * @return An index table mapping keys to their indices in the routing table.
        */
        constexpr index_table_t make_index_table() const;

        /**
        * 
        * @brief Helper function to create the index table using a compile-time index sequence.
        * This function generates the index table by iterating over the indices of the derived types.
        * 
        * @tparam Is The indices of the derived types.
        * @return An index table mapping keys to their indices in the routing table.
        */
        template <std::size_t... Is>
        constexpr index_table_t make_index_table_impl(std::index_sequence<Is...>) const;


        /**
        * @brief The routing table containing function pointers for each derived type.
        * 
        * This table is used to route calls to the appropriate getter, constructor, and destructor
        * for each derived type based on its key.
        */
        routing_table_t _routing_table = make_routing_table();


        /**
        * @brief The index table mapping keys to their corresponding indices in the routing table.
        * 
        * This table allows for fast lookups of routes by key, enabling efficient access to the
        * getter, constructor, and destructor functions for each derived type.
        */
        index_table_t _index_table = make_index_table();
    };
}

#include "registry.tpp"
#endif // ETASK_TOOLS_REGISTRY_HPP_