//! etask:doc file cf8107bf8261
/**
* @file context.hpp
*
* @brief Local context for the `n0` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_MESH_S4_N0_CONTEXT_HPP_
#define SYS_MESH_S4_N0_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
#include "p0/context.hpp"  //! etask:item p0
#include "p1/context.hpp"  //! etask:item p1
#include "p2/context.hpp"  //! etask:item p2
//! etask:end child_includes

namespace sys::mesh::s4::n0 {
    //! etask:doc class 04529f27d364
    /**
    * @brief Shared state and hardware for the `n0` scope - one node within a segment
    *
    * Injected by reference into every task in `sys::mesh::s4::n0`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        p0::context p0;  //! etask:item p0
        p1::context p1;  //! etask:item p1
        p2::context p2;  //! etask:item p2
        //! etask:end children
    };
} // namespace sys::mesh::s4::n0
#endif // SYS_MESH_S4_N0_CONTEXT_HPP_
