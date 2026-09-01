//! etask:doc file 05bfb2bf3847
/**
* @file context.hpp
*
* @brief Local context for the `s2` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_MESH_S2_CONTEXT_HPP_
#define SYS_MESH_S2_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
#include "n0/context.hpp"  //! etask:item n0
#include "n1/context.hpp"  //! etask:item n1
#include "n2/context.hpp"  //! etask:item n2
#include "n3/context.hpp"  //! etask:item n3
//! etask:end child_includes

namespace sys::mesh::s2 {
    //! etask:doc class e26c171bef39
    /**
    * @brief Shared state and hardware for the `s2` scope - one mesh segment
    *
    * Injected by reference into every task in `sys::mesh::s2`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        n0::context n0;  //! etask:item n0
        n1::context n1;  //! etask:item n1
        n2::context n2;  //! etask:item n2
        n3::context n3;  //! etask:item n3
        //! etask:end children
    };
} // namespace sys::mesh::s2
#endif // SYS_MESH_S2_CONTEXT_HPP_
