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
    unsigned short mLen;
    char mData[RDA_LOG_BUFSIZ];
};

static Buffer *sSpewQueue = NULL;
static Buffer *sFreeList = NULL;
static Buffer sStaticBuffers[RDA_LOG_NBUFFERS];
static bool sShouldTerminate = false;
static bool sHasTerminated = false;
static boost::mutex sBufferMutex;
static boost::once_flag sInitialized = BOOST_ONCE_INIT;

// We need to add behavior to boost::condition_variable's destructor.
class MyConditionVariable: public boost::condition_variable {
public:
    ~MyConditionVariable() {
        rda::log::terminate();
    }
};

//static boost::condition_variable sLogWakeup;
static MyConditionVariable sLogWakeup;
static boost::condition_variable sLogFinished;
static boost::thread sLogThread;

// Forward declarations
static void logThreadFunction();

static void init() {
    // Set up the free list and start the log thread
    std::cerr << "init() called." << std::endl;
    boost::lock_guard<boost::mutex> lock(sBufferMutex);
    sStaticBuffers[0].mNext = NULL;
    sStaticBuffers[0].mIndex = 1;
    for (unsigned i = 1; i < RDA_LOG_NBUFFERS; i++) {
        sStaticBuffers[i].mNext = sStaticBuffers + i - 1;
        sStaticBuffers[i].mIndex = i + 1;
    }
    sFreeList = sStaticBuffers + RDA_LOG_NBUFFERS - 1;
    // start the log thread
    sLogThread = boost::thread(logThreadFunction);
}

static void logThreadFunction() {
    std::cerr << "Enter logThreadFunction()" << std::endl;
    while (!sShouldTerminate) {
        {
            boost::unique_lock<boost::mutex> lock(sBufferMutex);
            while (sSpewQueue == NULL && !sShouldTerminate) {
                sLogWakeup.wait(lock);
            }
        }
        std::cerr << "logThreadFunction(): wakeup" << std::endl;
        rda::log::flush();
    }
    std::cerr << "Exit logThreadFunction()" << std::endl;
    sHasTerminated = true;
    sLogFinished.notify_all();
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
static NoLogStreamBuf sNoLogBuf;
static std::ostream sNoLogStream(&sNoLogBuf);

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

static int sLevel = rda::log::Info;
static const char *sLevelNames[] = {
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
static boost::thread_specific_ptr<LogStream> sThreadLogStream;

// Log constructor is the primary entry point into this code.
Log::Log(int level, const char *modfile, const char *function, int line) {
    if (level <= sLevel) {
        //static boost::thread_specific_ptr<LogStream> sThreadLogStream;
        _os = sThreadLogStream.get();
        if (_os == NULL) {
            boost::call_once(sInitialized, init);
            LogStream *ls = new LogStream;
            sThreadLogStream.reset(ls);
            _os = ls;
        }
        *_os << "timestamp " << sLevelNames[level] << " ["
            << modfile << ">" << function << ">" << line << "] ";
    }
    else _os = &sNoLogStream;
}

void setLogLevel(int level) {
    sLevel = level;
}

void flush() {
    // TODO merge this function into the log thread
    int count = 20;
    Buffer *buf = NULL;
    while (sSpewQueue != NULL || buf != NULL) {
        {
            boost::lock_guard<boost::mutex> lock(sBufferMutex);
            if (buf != NULL) {
                buf->mNext = sFreeList;
                sFreeList = buf;
            }
            buf = sSpewQueue;
            if (buf != NULL) {
                Buffer **prevLink = &sSpewQueue;
                while (buf->mNext != NULL) {
                    prevLink = &buf->mNext;
                    buf = buf->mNext;
                }
                *prevLink = NULL;
            }
        }
        if (buf != NULL) {
            // TODO write the exact length instead
            buf->mData[buf->mLen] = '\0';
            std::cerr << buf->mData;
        }
        count--;
        if (count <= 0) {
            std::cerr << "*** break out of flush()" << std::endl;
            break;
        }
    }
    // if writing to a real file, flush here
}

// Call this to get a clean exit.
// May be called multiple times.
// May be called from static destructors etc.
void terminate() {
    if (sHasTerminated) return;
    sShouldTerminate = true;
    sLogWakeup.notify_one();
    boost::unique_lock<boost::mutex> lock(sBufferMutex);
    sLogFinished.wait(lock);
}

void debug(const char *message) {
    std::cerr << message << " FreeList:";
    boost::lock_guard<boost::mutex> lock(sBufferMutex);
    int count = 20;
    for (Buffer *buf = sFreeList; buf; buf = buf->mNext) {
        std::cerr << " " << buf->mIndex;
        count--;
        if (count <= 0) {
            std::cerr << "\n*** break out of debug()" << std::endl;
            break;
        }
    }
    count = 20;
    std::cerr << " SpewQueue:";
    for (Buffer *buf = sSpewQueue; buf; buf = buf->mNext) {
        std::cerr << " " << buf->mIndex;
        count--;
        if (count <= 0) {
            std::cerr << "\n*** break out of debug()" << std::endl;
            break;
        }
    }
    std::cerr << std::endl;
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
        boost::lock_guard<boost::mutex> lock(sBufferMutex);
        mBuf = sFreeList;
        if (mBuf != NULL) sFreeList = mBuf->mNext;
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
        else {
            boost::lock_guard<boost::mutex> lock(sBufferMutex);
            mBuf->mNext = sFreeList;
            sFreeList = mBuf;
        }
    }
}

int LogStreamBuf::sync()
{
    // Make sure it ends in a newline.
    char *p = pptr();
    if (p <= mBuf->mData) return 0;
    if (p[-1] != '\n') *p++ = '\n';
    mBuf->mLen = p - mBuf->mData;
    bool needToNotify = false;
    {
        boost::lock_guard<boost::mutex> lock(sBufferMutex);
        if (mBuf != NULL) {
            mBuf->mNext = sSpewQueue;
            sSpewQueue = mBuf;
            needToNotify = true;
        }
        mBuf = sFreeList;
        if (mBuf != NULL) sFreeList = mBuf->mNext;
        //else // TODO increment a counter
    }
    if (needToNotify) {
        sLogWakeup.notify_one();
    }
    if (mBuf != NULL) {
        setp(mBuf->mData, mBuf->mData + RDA_LOG_BUFSIZ - 2);
    } else {
        setp(0, 0);
    }
    return 0;
}

int LogStreamBuf::overflow(int c)
{
    // client tries to write more than a buffer full
    // TODO increment a counter

    // for now, truncate but do not error
    return c;
}


