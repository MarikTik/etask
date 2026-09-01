//! etask:doc file 9eb21bfe27bc
/**
* @file context.hpp
*
* @brief Local context for the `scalars` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
//! etask:end doc file
#ifndef SYS_SCALARS_CONTEXT_HPP_
#define SYS_SCALARS_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
//! etask:end child_includes

namespace sys::scalars {
    //! etask:doc class 60e9a099696a
    /**
    * @brief Shared state and hardware for the `scalars` scope - one task per scalar type in TypeMap
    *
    * Every type the schema's TypeMap admits, returned where a width or
    * endianness error cannot hide. Split by signedness and by float/integer
    * rather than crammed into one shape, because a single wide shape would let a
    * misread field be absorbed by its neighbour: read int16 as int32 inside one
    * packed struct and every later field shifts, which is loud; read it wrong
    * when it is the *only* field and the frame is still the right length.
    *
    * Injected by reference into every task in `sys::scalars`,
    * which may also reach into the child-scope contexts it holds.
    */
    //! etask:end doc class
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        //! etask:end children
    };
} // namespace sys::scalars
#endif // SYS_SCALARS_CONTEXT_HPP_
