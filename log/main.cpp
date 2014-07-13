#include "log.hpp"
#include "boost/thread/thread.hpp"

#if 1
#define PAUSE \
    boost::this_thread::sleep(boost::posix_time::millisec(100))
#else
#define PAUSE while(0)
#endif

void threadFunction(const char *name, int count) {
    while (count > 0) {
        LOG_ERROR << name << " " << count;
        boost::this_thread::sleep(boost::posix_time::millisec(200));
        count--;
    }
}

int main() {
    rda::log::debug("begin");
    LOG_DEBUG << "This is a debug message.";
    rda::log::debug("debug");
    PAUSE;
    LOG_ALWAYS << "This is an Always message.";
    rda::log::debug("always");
    PAUSE;
    LOG_ERROR << "This is an Error message";
    rda::log::debug("error");
    PAUSE;
    LOG_WARN << "This is a Warning message";
    rda::log::debug("warn");
    PAUSE;
    LOG_INFO << "This is an Info message";
    rda::log::debug("info");
    PAUSE;
    LOG_VERBOSE << "This is a Verbose message";
    rda::log::debug("verbose");
    PAUSE;
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
    PAUSE;
    boost::thread t(threadFunction, "the one", 10);
    t.join();
    rda::log::terminate();
}

