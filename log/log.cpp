// log.cpp

#include <boost/thread.hpp>
#include "log.hpp"

#ifndef RDA_LOG_BUFSIZ
#define RDA_LOG_BUFSIZ 200
#endif

#ifndef RDA_LOG_NBUFFERS
#define RDA_LOG_NBUFFERS 3
#endif

namespace {

// Management of log buffers:
// RDA_LOG_NBUFFERS of them are statically allocated,
// and more may be allocated from the heap as needed.
// They are never freed.
//
// When a log message is complete, the client thread puts it into the
// "spew queue", notifies the log thread, and grabs an empty buffer.  
// If no empty buffer is available, the client keeps its buffer to
// re-use and the message is lost.
// The buffers are kept as singly-linked lists with an embedded "next"
// pointer.

struct Buffer {
    Buffer *mNext;
    int mIndex;
    char mData[RDA_LOG_BUFSIZ];
};

static Buffer *s_spewQueue = NULL;
static Buffer *s_freeList = NULL;
static Buffer s_staticBuffers[RDA_LOG_NBUFFERS];
static boost::mutex s_bufferMutex;

static void init() {
    // Set up the free list and start the log thread
    std::cerr << "init() called." << std::endl;
    // TODO move this outside the function
    static unsigned alreadyInitialized;
    const unsigned magic = 0x6e71057;
    if (alreadyInitialized == magic) return;
    std::cerr << "initializing." << std::endl;
    boost::lock_guard<boost::mutex> lock(s_bufferMutex);
    s_staticBuffers[0].mNext = NULL;
    s_staticBuffers[0].mIndex = 1;
    for (unsigned i = 1; i < RDA_LOG_NBUFFERS; i++) {
        s_staticBuffers[i].mNext = s_staticBuffers + i - 1;
        s_staticBuffers[i].mIndex = i + 1;
    }
    s_freeList = s_staticBuffers + RDA_LOG_NBUFFERS - 1;
    // TODO start the log thread
}

// To specialize std::streambuf for output only, we need to specialize
//   sync() - called to flush, e.g. from std::endl
//   overflow() - called when pptr() == epptr()
//   xsputn() - for efficiency

// This stream buffer throws away the data but pretends to write it.
// Useful for logging that is filtered out at runtime.

class NoLogStreamBuf: public std::streambuf {
public:
    NoLogStreamBuf() { }
    virtual ~NoLogStreamBuf() { }
private:
    virtual int sync() { return 0; }
    virtual std::streamsize xsputn(const char *s, std::streamsize n)
            { return n; }
    virtual int overflow(int c) { return c; }
};

// The single global NoLogStream used whenever a log message is filtered
// out at runtime.
static NoLogStreamBuf s_noLogBuf;
static std::ostream s_noLogStream(&s_noLogBuf);

class LogStreamBuf: public std::streambuf {
public:
    LogStreamBuf();
    virtual ~LogStreamBuf();
private:
    virtual int sync(); // return 0/-1
    //virtual std::streamsize xsputn(const char *s, std::streamsize n);
    virtual int overflow(int c); // return c or EOF
    Buffer *mBuf;
};

class LogStream: public std::ostream {
    LogStreamBuf _buf;  // This is OK
public:
    LogStream()
    : std::ostream(&_buf)
    { }

    virtual ~LogStream() { }
};

static int s_level = rda::log::Info;
static const char *s_levelNames[] = {
    // These had better match the enum or havoc will ensue!
    "Always",
    "Error",
    "Warn",
    "Info",
    "Verbose",
};

};  // end anonymous namespace

namespace rda {
namespace log {

// The global NullStream instance
rda::log::NullStream null;

// The per-thread LogStream instance
//static boost::thread_specific_ptr<LogStream> s_threadLogStream;

// Log constructor is the primary entry point into this code.
Log::Log(int level, const char *modfile, const char *function, int line) {
    if (level <= s_level) {
        static boost::thread_specific_ptr<LogStream> s_threadLogStream;
        _os = s_threadLogStream.get();
        if (_os == NULL) {
            init();
            LogStream *ls = new LogStream;
            s_threadLogStream.reset(ls);
            _os = ls;
        }
        *_os << "timestamp " << s_levelNames[level] << " ["
            << modfile << ">" << function << ">" << line << "] ";
    }
    else _os = &s_noLogStream;
}

void setLogLevel(int level) {
    s_level = level;
}

void flush() {
    // TODO morph this function into the log thread
    int count = 20;
    while (s_spewQueue != NULL) {
        Buffer *buf;
        {
            boost::lock_guard<boost::mutex> lock(s_bufferMutex);
            buf = s_spewQueue;
            if (buf != NULL) {
                Buffer **prevLink = &s_spewQueue;
                while (buf->mNext != NULL) {
                    prevLink = &buf->mNext;
                    buf = buf->mNext;
                }
                *prevLink = NULL;
            }
        }
        if (buf != NULL) {
            std::cerr << buf->mData;
            boost::lock_guard<boost::mutex> lock(s_bufferMutex);
            buf->mNext = s_freeList;
            s_freeList = buf;
        }
        count--;
        if (count <= 0) {
            std::cerr << "*** break out of flush()" << std::endl;
            break;
        }
    }
}

void debug(const char *message) {
    std::cerr << message << std::endl;
    boost::lock_guard<boost::mutex> lock(s_bufferMutex);
    int count = 20;
    for (Buffer *buf = s_freeList; buf; buf = buf->mNext) {
        std::cerr << "FreeList buffer " << buf->mIndex << std::endl;
        count--;
        if (count <= 0) {
            std::cerr << "*** break out of debug()" << std::endl;
            break;
        }
    }
    for (Buffer *buf = s_spewQueue; buf; buf = buf->mNext) {
        std::cerr << "SpewQueue buffer " << buf->mIndex << std::endl;
        count--;
        if (count <= 0) {
            std::cerr << "*** break out of debug()" << std::endl;
            break;
        }
    }
}

}  // end namespace log
}  // end namespace rda

LogStreamBuf::LogStreamBuf()
{
    // set up pointers with a call to
    // setg(NULL, NULL, NULL) (input pointers) and
    // setp(begin, end) (output pointers)
    setg(NULL, NULL, NULL);
    {
        boost::lock_guard<boost::mutex> lock(s_bufferMutex);
        mBuf = s_freeList;
        if (mBuf != NULL) s_freeList = mBuf->mNext;
        //else // TODO increment error counter
    }
    if (mBuf != NULL) {
        // leave room for a newline
        setp(mBuf->mData, mBuf->mData + RDA_LOG_BUFSIZ - 2);
    } else {
        setp(0, 0);
    }
}

LogStreamBuf::~LogStreamBuf()
{
    if (mBuf != NULL) {
        if (pptr() > mBuf->mData) sync();
        boost::lock_guard<boost::mutex> lock(s_bufferMutex);
        mBuf->mNext = s_freeList;
        s_freeList = mBuf;
    }
}

int LogStreamBuf::sync()
{
    // TODO Make sure it ends in a newline.
    {
        boost::lock_guard<boost::mutex> lock(s_bufferMutex);
        if (mBuf != NULL) {
            mBuf->mNext = s_spewQueue;
            s_spewQueue = mBuf;
        }
        mBuf = s_freeList;
        if (mBuf != NULL) s_freeList = mBuf->mNext;
        //else // TODO increment a counter
    }
    if (mBuf != NULL) {
        setp(mBuf->mData, mBuf->mData + RDA_LOG_BUFSIZ - 2);
    } else {
        setp(0, 0);
    }
}

int LogStreamBuf::overflow(int c)
{
    // client tries to write more than a buffer full
    // TODO increment a counter

    // for now, truncate but do not error
    return c;
}


