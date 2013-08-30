#define BOOST_TEST_MODULE atom test
#include <boost/test/unit_test.hpp>

#define RDA_ATOM_COUNT
#include "atom.hpp"

using namespace std;
using namespace rda;

BOOST_AUTO_TEST_CASE(atom)
{
    BOOST_CHECK_EQUAL( 0, Atom::constructor_count );
    Atom a1;
    BOOST_CHECK_EQUAL( 0, Atom::constructor_count );
    BOOST_CHECK_NO_THROW( cout << "a1 is " << a1 << endl );
    BOOST_CHECK_NO_THROW( a1 = "hello" );
    BOOST_CHECK_EQUAL( 0, Atom::constructor_count );
    BOOST_CHECK_NO_THROW( cout << "a1 is " << a1 << endl );
    BOOST_CHECK_NO_THROW( a1 = Atom("goodbye") );
    BOOST_CHECK_EQUAL( 1, Atom::constructor_count );
    BOOST_CHECK_NO_THROW( cout << "a1 is " << a1 << endl );
    Atom a2 = "another";
    BOOST_CHECK_EQUAL( 2, Atom::constructor_count );
    BOOST_CHECK_NE( a1, Atom("hello") );
    BOOST_CHECK_EQUAL( 3, Atom::constructor_count );
    BOOST_CHECK_NE( a1, a2 );
    BOOST_CHECK_EQUAL( a1, Atom("goodbye") );
    BOOST_CHECK_EQUAL( 4, Atom::constructor_count );
    cout << "Loop 1:" << endl;
    for (int i = 0; i < 10; i++) {
        BOOST_CHECK_EQUAL( a2, Atom("another") );
    }
    cout << "constructor count: " << Atom::constructor_count << endl;
    cout << "Loop 2:" << endl;
    for (int i = 0; i < 10; i++) {
        if (a2 == Atom("another")) cout << "eq ";
        else cout << "ne ";
    }
    cout << endl;
    cout << "constructor count: " << Atom::constructor_count << endl;
    cout << "Loop 3:" << endl;
    for (int i = 0; i < 10; i++) {
        if (a2 == "another") cout << "eq ";
        else cout << "ne ";
    }
    cout << endl;
    cout << "constructor count: " << Atom::constructor_count << endl;
}

