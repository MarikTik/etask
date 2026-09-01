//! etask:doc file 5e3125fbb7db
/**
* @file context.hpp
*
* @brief Local context for the `mesh` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_MESH_CONTEXT_HPP_
#define SYS_MESH_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
#include "s0/context.hpp"  //! etask:item s0
#include "s1/context.hpp"  //! etask:item s1
#include "s2/context.hpp"  //! etask:item s2
#include "s3/context.hpp"  //! etask:item s3
#include "s4/context.hpp"  //! etask:item s4
#include "s5/context.hpp"  //! etask:item s5
//! etask:end child_includes

namespace sys::mesh {
    //! etask:doc class 27be3b0f131f
    /**
    * @brief Shared state and hardware for the `mesh` scope - the segmented probe mesh
    *
    * Six segments, each holding four nodes, each holding three probes. The
    * shape is arbitrary; the point is that one definition fans out to 288
    * tasks whose uids, contexts, and namespaces are all distinct.
    *
    * Injected by reference into every task in `sys::mesh`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        s0::context s0;  //! etask:item s0
        s1::context s1;  //! etask:item s1
        s2::context s2;  //! etask:item s2
        s3::context s3;  //! etask:item s3
        s4::context s4;  //! etask:item s4
        s5::context s5;  //! etask:item s5
        //! etask:end children
    };
} // namespace sys::mesh
#endif // SYS_MESH_CONTEXT_HPP_
