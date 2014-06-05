
#include "component.hpp"
#include <iostream>
#include <sstream>

using namespace std;

namespace {

class OtherImpl: public OtherInterface {
public:
    std::string bfn(float f) {
        ostringstream ostr;
        ostr << "My favorite number is " << f;
        return ostr.str();
    }
};

class ThirdImpl: public ThirdInterface {
public:
    virtual float cfn(float f) { return f * 0.5; }
};

class MyComponentImpl: public MyComponent, public TheInterface {
public:
    virtual void afn1(int i) { m_n += i; }

    virtual int afn2() { return m_n; }

    virtual TheInterface* getTheInterface() { return this; }

    virtual OtherInterface* getOtherInterface() {
        if (NULL == m_pOther) {
            m_pOther = new OtherImpl;
        }
        return m_pOther;
    }

    virtual ThirdInterface* getThirdInterface() { return &m_third; }

    virtual ~MyComponentImpl() { }

    MyComponentImpl(int n) : m_n(n), m_pOther(NULL) { }

    int m_n;
    OtherInterface *m_pOther;
    ThirdImpl m_third;

};

}  // end of anonymous namespace

MyComponent* MyComponent::factory(int n) {
    return new MyComponentImpl(n);
}

