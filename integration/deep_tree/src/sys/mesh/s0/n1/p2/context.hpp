//! etask:doc file 22fdecc8ca16
/**
* @file context.hpp
*
* @brief Local context for the `p2` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_MESH_S0_N1_P2_CONTEXT_HPP_
#define SYS_MESH_S0_N1_P2_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::mesh::s0::n1::p2 {
    //! etask:doc class 29a2ab6e881c
    /**
    * @brief Shared state and hardware for the `p2` scope - one probe on a node
    *
    * Injected by reference into every task in `sys::mesh::s0::n1::p2`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::mesh::s0::n1::p2
#endif // SYS_MESH_S0_N1_P2_CONTEXT_HPP_
