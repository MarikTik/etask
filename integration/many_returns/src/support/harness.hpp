/**
* @file harness.hpp
*
* @brief The scripted request sequence, and the reply frames it produces.
*
* @note User-owned (support/). Not generated.
*
* ## What this is for
*
* `verify.py` needs the exact bytes this firmware would put on the wire for a
* known sequence of requests. It cannot get them by reasoning about the schema -
* that would be re-implementing the thing under test - so the firmware produces
* them and prints them.
*
* Each case is one request in and (usually) one reply out. The reply is printed
* whole, header included, as a single hex line tagged with the case's name:
*
* ```
* case unsigned_widths 0400...
* ```
*
* A case that produces *no* reply prints its tag with an empty frame, so a
* missing reply is a line the driver can assert on rather than an absence it has
* to notice. Everything else - what the bytes should be - lives on the host side,
* which is the only place an expectation is worth anything.
*
* ## Why it lives beside the firmware rather than in the test
*
* The sequence is firmware behaviour: which task, in which order, with which
* arguments. Writing it here keeps `verify.py` a decoder and an assertion list,
* with no idea how a request is built - so a change to the request layout breaks
* the build rather than quietly making the driver test nothing.
*/
#ifndef SUPPORT_HARNESS_HPP_
#define SUPPORT_HARNESS_HPP_

namespace support {

    /**
    * @class harness
    *
    * @brief Drives every case in this project's reply-direction test.
    *
    * Stateless: all the state is in `config::`, and the sequence is a single
    * pass. Held as a class rather than a free function only to keep the case
    * helpers off the enclosing namespace.
    */
    class harness {
    public:
        /**
        * @brief Runs every case, printing one tagged hex line per reply.
        *
        * Cases run in a fixed order and each waits for its own reply before the
        * next begins, so the transcript is deterministic and a driver can match
        * lines by tag rather than by position.
        */
        static void run();

    private:
        /// @brief The scalar round-trip cases: one per width class.
        static void scalars();

        /// @brief The tasks that reply with a status and no result bytes.
        static void nothing();

        /// @brief The widest declared shape, which sizes the reply frame.
        static void wide();

        /// @brief Every branch of every status-keyed task.
        static void keyed();
    };

} // namespace support

#endif // SUPPORT_HARNESS_HPP_
