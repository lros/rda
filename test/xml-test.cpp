
#include <iostream>
#include <rdaxml.hpp>

using namespace std;
using namespace rda::xml;

void test() {
    Element outer(cout, "foo");
    Attribute(outer, "a1") << "val1";
    Attribute(outer, "a2");
    outer.attribute("a3") << 37;
    outer << "\nHere's a complex inner element:\n";
    {
        Element inner(outer, "bar");
        inner << "inner ";
        Element(inner, "empty_tag");
        inner << " body";
    }
    outer << "\nHere's an empty-element tag with attribute:\n";
    Element(outer, "empty_attr").attribute("attr") << "value";
    outer << "\nAnd a one-liner inner element with content:\n";
    Element(outer, "baz") << "baz's content";
    outer << "\n";
}

int main () {
    test();
    cout << endl;
}
