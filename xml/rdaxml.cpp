
#include <stdexcept>
#include "rdaxml.hpp"

using namespace std;

namespace rda {
namespace xml {

void Element::start()
{
    m_out << "<" << m_name;
}

ostream &Element::contentOut() {
    attrEnd();
    if (m_state == kName) {
        m_out << ">";
        m_state = kContent;
    }
    return m_out;
}

Element::~Element() {
    if (m_state == kName) {
        m_out << " />";
    } else {
        m_out << "</" << m_name << ">";
    }
}

void Element::attrBegin(const char *name) {
    if (m_state != kName) throw logic_error("xml attribute after content");
    m_out << " " << name;
}

ostream &Element::attrValueOut() {
    m_out << "=\"";
    m_state = kAttr;
    return m_out;
}

void Element::attrEnd() {
    if (m_state == kAttr) {
        m_out << "\"";
        m_state = kName;
    }
}

}  // end namespace xml
}  // end namespace rda

