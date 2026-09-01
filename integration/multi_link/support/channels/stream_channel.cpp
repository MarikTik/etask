/**
* @file stream_channel.cpp
*
* @brief The descriptor I/O behind @ref support::channels::stream_channel.
*
* @note User-owned support code. Kept out of the header because these three
*       functions are the only part of the transport that touches POSIX, and a
*       board port replaces this translation unit alone - the record framing in
*       the header is medium-independent and should not have to be revisited.
*/
#include "support/channels/stream_channel.hpp"
#include <unistd.h>
#include <cerrno>

namespace support::channels {

    bool stream_channel::fill(std::size_t needed) noexcept
    {
        while (_held < needed) {
            const ::ssize_t got = ::read(_fd, _buffer + _held, needed - _held);

            // Zero means the peer closed: there will never be more bytes, so the
            // partial record already buffered is now unfillable. Reported the same
            // as "not yet" rather than as an error, because this channel's caller
            // polls and has no error path - a closed link simply goes quiet, which
            // is what a dropped wire looks like anyway.
            if (got == 0) return false;

            if (got < 0) {
                // EINTR is not a failure, just an interrupted syscall; retrying is
                // the whole handling. EAGAIN on a non-blocking fd means the rest of
                // the record has not arrived, which is the ordinary case this
                // buffering exists for.
                if (errno == EINTR) continue;
                return false;
            }

            _held += static_cast<std::size_t>(got);
        }
        return true;
    }

    void stream_channel::consume(std::size_t count) noexcept
    {
        _held -= count;
        if (_held > 0) std::memmove(_buffer, _buffer + count, _held);
    }

    bool stream_channel::write_all(const std::byte* bytes, std::size_t length) noexcept
    {
        std::size_t sent = 0;
        while (sent < length) {
            const ::ssize_t put = ::write(_fd, bytes + sent, length - sent);

            if (put < 0) {
                // A partial write is normal on a stream socket once the peer's
                // receive buffer fills; EAGAIN says to try the remainder later. The
                // loop spins rather than returning, because a half-written record
                // would desynchronise the fixed-size framing permanently - there is
                // no resync marker to recover on, so the record must go out whole.
                if (errno == EINTR or errno == EAGAIN or errno == EWOULDBLOCK) continue;
                return false;
            }
            sent += static_cast<std::size_t>(put);
        }
        return true;
    }

} // namespace support::channels
