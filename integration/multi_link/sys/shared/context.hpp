//! etask:doc file ac863c152fe3
/**
* @file context.hpp
*
* @brief Local context for the `shared` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_SHARED_CONTEXT_HPP_
#define SYS_SHARED_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes
#include <cstdint>

namespace sys::shared {
    //! etask:doc class 0393ae0c1507
    /**
    * @brief Shared state and hardware for the `shared` scope - carried by both links
    *
    * The control case. Because this subsystem is listed by both links, its uid must be accepted on either wire - which is what distinguishes a correct per-uid allowlist from a link that simply refuses whatever it does not exclusively own.
    *
    * Injected by reference into every task in `sys::shared`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        /**
        * @brief How many times a task in this scope has concluded.
        *
        * State rather than a constant because it is the one thing a reply can
        * report that a link *cannot* forge: the host drives this subsystem over
        * both links, and a counter that advances across both proves the two
        * channels reached the same device rather than two copies of it. A
        * per-link context would make both wires report `1` and the test would
        * pass against a board that had accidentally been built twice.
        */
        std::uint8_t served{0};

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::shared
#endif // SYS_SHARED_CONTEXT_HPP_
