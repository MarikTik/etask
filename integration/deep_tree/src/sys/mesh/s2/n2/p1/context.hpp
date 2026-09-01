//! etask:doc file bc0ecc39c0be
/**
* @file context.hpp
*
* @brief Local context for the `p1` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_MESH_S2_N2_P1_CONTEXT_HPP_
#define SYS_MESH_S2_N2_P1_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::mesh::s2::n2::p1 {
    //! etask:doc class 11da92298ed0
    /**
    * @brief Shared state and hardware for the `p1` scope - one probe on a node
    *
    * Injected by reference into every task in `sys::mesh::s2::n2::p1`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::mesh::s2::n2::p1
#endif // SYS_MESH_S2_N2_P1_CONTEXT_HPP_
