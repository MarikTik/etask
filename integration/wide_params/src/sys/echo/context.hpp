//! etask:doc file ce5199895313
/**
* @file context.hpp
*
* @brief Local context for the `echo` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_ECHO_CONTEXT_HPP_
#define SYS_ECHO_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::echo {
    //! etask:doc class 088e08ab0ed8
    /**
    * @brief Shared state and hardware for the `echo` scope - one task per scalar type, echoed back unchanged
    *
    * The per-type baseline. Each task takes exactly one value of one schema
    * type and returns it, so a mismatch localizes to that type immediately:
    * "int64 came back byte-swapped" rather than "the seventh field of the wide
    * frame is wrong".
    *
    * All twelve of TypeMap's types appear here, `int` included. `int` and
    * `int32` lower to the same C++ type (std::int32_t) and the same four wire
    * bytes - they are exercised separately anyway, because they are separate
    * *schema* spellings, and a generator that dropped one from its table would
    * still pass a test that only used the other.
    *
    * Injected by reference into every task in `sys::echo`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::echo
#endif // SYS_ECHO_CONTEXT_HPP_
