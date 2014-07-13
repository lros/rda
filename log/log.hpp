// log.hpp

// Features:
// + Debug logger compiles to nothing in release builds; in debug builds
//   its output is always present.
// + Log levels: verbose, normal, off
// + Module - typically the name of the directory containing the client
//   software, it is printed with each log message.
//
// Bonus feature:
// + Level can be set at runtime independently for each module.

/* API Design sketch
The log stream is like an ofstream but:
(a) it rotates its files
(b) it prints or discards data depending on the current log level setting
and the priority of the message
(c) it magically prints module, file, function, timestamp with each
output line and appends std::endl.
(d) it is thread-safe
(e) it is reasonable to log messages from real-time threads - if push
comes to shove, log messages are lost rather than block.

Debug log: in a production build, compile the entire statement away
into nothing by defining a type with operator << that does nothing.
In a release build, use the log stream.
*/

#include <iostream>

namespace rda {
namespace log {

// NullStream - it looks like an ostream at compile time, but does
// nothing and compiles to nothing.  However it really works right
// syntactically and if you perversely put in a function call, the
// function will be called.

class NullStream { };

template <typename T> NullStream & operator << (NullStream &null, T object) {
    return null;
}

extern NullStream null;

// Log - it looks like a function that returns an ostream, but in
// fact it's a constructor so there's a destructor called at the end
// of the expression.

struct Log {
    std::ostream *_os;
    Log(int level, const char *modFile, const char *function, int line);
    ~Log() { *_os << std::endl; }
};

template<typename T> std::ostream & operator << (Log log, T object) {
    return *log._os << object;
}

// Log levels
enum {
    Always = 0,
    Error,
    Warn,
    Info,
    Verbose
};

void setLogLevel(int level);
void flush();    // TODO remove this
void debug(const char *message);    // TODO remove this
void terminate();

}  // end namespace log
}  // end namespace rda

#ifdef DEBUG_BUILD

#define LOG_DEBUG rda::log::Log(rda::log::Always, \
        RDA_MODULE ">" __FILE__, __FUNCTION__, __LINE__)

#else

#define LOG_DEBUG rda::log::null

#endif

#define LOG_ALWAYS rda::log::Log(rda::log::Always, \
        RDA_MODULE ">" __FILE__, __FUNCTION__, __LINE__)

#define LOG_ERROR rda::log::Log(rda::log::Error, \
        RDA_MODULE ">" __FILE__, __FUNCTION__, __LINE__)

#define LOG_WARN rda::log::Log(rda::log::Warn, \
        RDA_MODULE ">" __FILE__, __FUNCTION__, __LINE__)

#define LOG_INFO rda::log::Log(rda::log::Info, \
        RDA_MODULE ">" __FILE__, __FUNCTION__, __LINE__)

#define LOG_VERBOSE rda::log::Log(rda::log::Verbose, \
        RDA_MODULE ">" __FILE__, __FUNCTION__, __LINE__)

