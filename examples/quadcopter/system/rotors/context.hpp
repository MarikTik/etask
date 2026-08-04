// SPDX-License-Identifier: MIT
/**
* @file context.hpp
*
* @brief Local context for the `rotors` scope (state, hardware, child contexts).
*
* @note Generated once by etask, then owned by you - EXCEPT the
*       `//! etask:managed` regions, which the generator keeps in step with
*       the schema (child contexts added/removed as scopes change). Add your
*       own state outside those regions; it is never overwritten.
*/
#ifndef SYSTEM_ROTORS_CONTEXT_HPP_
#define SYSTEM_ROTORS_CONTEXT_HPP_
//! etask:managed child_includes - child subsystem context headers
#include "fl/context.hpp"  //! etask:item fl
#include "fr/context.hpp"  //! etask:item fr
#include "rl/context.hpp"  //! etask:item rl
#include "rr/context.hpp"  //! etask:item rr
//! etask:end child_includes

namespace system::rotors {
    /**
    * @brief Shared state and hardware for the `rotors` scope - the four-rotor array
    *
    * The lift plant. Each rotor is an ESC-driven brushless motor; all four are
    * commanded together every control tick, so set_thrust is concurrent.
    *
    * Injected by reference into every task in `system::rotors`,
    * which may also reach into the child-scope contexts it holds.
    */
    struct context {
        // Add this scope's own hardware handles / state here.

        //! etask:managed children - child subsystem contexts
        fl::context fl;  //! etask:item fl
        fr::context fr;  //! etask:item fr
        rl::context rl;  //! etask:item rl
        rr::context rr;  //! etask:item rr
        //! etask:end children
    };
} // namespace system::rotors
#endif // SYSTEM_ROTORS_CONTEXT_HPP_
