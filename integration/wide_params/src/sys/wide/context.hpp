//! etask:doc file 41a918b28349
/**
* @file context.hpp
*
* @brief Local context for the `wide` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_WIDE_CONTEXT_HPP_
#define SYS_WIDE_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::wide {
    //! etask:doc class 37d9f2c422f2
    /**
    * @brief Shared state and hardware for the `wide` scope - the widest parameter lists a frame carries
    *
    * Nothing in the schema caps a parameter list: `generated/links.hpp` sizes
    * every frame from the widest task in the project, so a longer list makes a
    * bigger frame rather than an error. The cap is therefore a decision, and
    * this project makes it explicitly - see `everything` below.
    *
    * Injected by reference into every task in `sys::wide`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::wide
#endif // SYS_WIDE_CONTEXT_HPP_
