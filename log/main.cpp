#include "log.hpp"

int main() {
    rda::log::debug("begin");
    LOG_DEBUG << "This is a debug message.";
    rda::log::debug("debug");
    LOG_ALWAYS << "This is an Always message.";
    rda::log::debug("always");
    LOG_ERROR << "This is an Error message";
    rda::log::debug("error");
    LOG_WARN << "This is a Warning message";
    rda::log::debug("warn");
    LOG_INFO << "This is an Info message";
    rda::log::debug("info");
    LOG_VERBOSE << "This is a Verbose message";
    rda::log::debug("verbose");
    LOG_DEBUG << "This is a really long debug message that overflows.  "
        << "This is a really long debug message that overflows.  "
        << "This is a really long debug message that overflows.  "
        << "This is a really long debug message that overflows.  "
        << "This is a really long debug message that overflows.  "
        << "This is a really long debug message that overflows.  "
        << "This is a really long debug message that overflows.  "
        << "This is a really long debug message that overflows.  "
        << "This is a really long debug message that overflows.  "
        << "This is a really long debug message that overflows.  "
        << "This is a really long debug message that overflows.  "
        << "This is a really long debug message that overflows.  "
        << "This is a really long debug message that overflows.  "
        << "This is a really long debug message that overflows.  "
        << "This is a really long debug message that overflows.  ";
    rda::log::debug("debug (long)");
    rda::log::flush();
    rda::log::debug("flush");
}

