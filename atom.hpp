// atom.hpp
// Part of Rda framework.

#ifndef ATOM_HPP_INLUDE_GUARD
#define ATOM_HPP_INLUDE_GUARD

#include <iostream>

namespace rda {

class Atom {
    unsigned value;
    static unsigned atomValue(const char *str);
    static const char *atomName(unsigned value);
public:
    Atom(const char *str)
    : value(atomValue(str))
    #ifdef RDA_ATOM_COUNT
        { constructor_count++; }
        static unsigned constructor_count;
    #else
        { }
    #endif

    Atom() : value(0) { }

    Atom &operator = (const char *str) {
        value = atomValue(str);
        return *this;
    }

    bool operator == (const Atom &a) const
    { return value == a.value; }

    bool operator == (const char *str) const
    // TODO Um, is this really what we want?
    // Creates a new atom if str is new.
    // Alternative is to do strcmp(atomName(value), str).
    { return value == atomValue(str); }

    operator const char * () const
    { return atomName(value); }

    //const char *name() const
    //{ return atomName(value); }

};  // end class rda::Atom

#ifdef RDA_ATOM_COUNT
    unsigned Atom::constructor_count = 0;
#endif

}  // end namespace rda

//inline std::ostream &operator << (std::ostream &out, const rda::Atom &a)
//{ return out << a.name(); };

#endif  // ATOM_HPP_INCLUDE_GUARD

