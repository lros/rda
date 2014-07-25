
#ifndef RDAXML_HPP
#define RDAXML_HPP

#include <iostream>

namespace rda {
namespace xml {

class Element;

// TODO Abolish assignment operator (and copy constructor?)
class Attribute {
public:
    Attribute(Element &elem, const char *name);
    std::ostream &valueOut() const;
    ~Attribute();
private:
    Element &m_elem;
};

// TODO Abolish assignment operator (and copy constructor?)
class Element {
    friend class Attribute;
public:
    Element(std::ostream &os, const char *name);
    Element(Element &elem, const char *name);
    Attribute attribute(const char *name);
    std::ostream &contentOut();
    ~Element();
private:
    void start();
    void attrBegin(const char *name);
    std::ostream &attrValueOut();
    void attrEnd();

    std::ostream &m_out;
    const char *m_name;
    enum { kName, kAttr, kContent } m_state;
};  // end class Element

inline Element::Element(std::ostream &os, const char *name)
    : m_out(os), m_state(kName), m_name(name) { start(); }
inline Element::Element(Element &elem, const char *name)
    : m_out(elem.contentOut()), m_state(kName), m_name(name) { start(); }
inline Attribute Element::attribute(const char *name)
    { return Attribute(*this, name); }

template<typename T>
std::ostream& operator<< (const Element &elem, T &arg) {
    return const_cast<Element &>(elem).contentOut() << arg;
}

inline Attribute::Attribute(Element &elem, const char *name)
    : m_elem(elem) { m_elem.attrBegin(name); }
inline std::ostream &Attribute::valueOut() const
    { return m_elem.attrValueOut(); }
inline Attribute::~Attribute()
    { m_elem.attrEnd(); }

template<typename T>
std::ostream& operator<< (const Attribute &attr, T arg) {
    return attr.valueOut() << arg;
}

}  // end namespace rda::xml
}  // end namespace rda

#endif  // RDAXML_HPP
