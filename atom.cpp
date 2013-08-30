// atom.cpp
// Part of Rda framework

#include "atom.hpp"
#include <map>
#include <vector>
#include <stdexcept>

using namespace std;

namespace {

const char *const undefinedAtom = "undefined rda::Atom";
typedef map<const char *, unsigned> S2A;
static S2A *s2a;
typedef vector<const char *> A2S;
static A2S *a2s;

}  // end anonymous namespace

namespace rda {

unsigned Atom::atomValue(const char *str) {
    const unsigned kInitialized = 0x1a2b3c4d;
    static unsigned initialized;
    // TODO grab a scoped lock
    if (initialized != kInitialized) {
        s2a = new S2A;
        a2s = new A2S;
        a2s->push_back(undefinedAtom);
        initialized = kInitialized;
    }
    unsigned &value = (*s2a)[str];
    if (0 == value) {
        value = a2s->size();
        a2s->push_back(strdup(str));
        cout << "new atom \"" << str << "\" = " << value << endl;
    }
    return value;
}

const char *Atom::atomName(unsigned value) {
    // TODO grab a scoped lock
    if (NULL == a2s) {
        if (0 == value) {
            return undefinedAtom;
        } else {
            throw logic_error("uninitialized Atom table");
        }
    }
    return (*a2s)[value];
}

}  // end namespace rda

