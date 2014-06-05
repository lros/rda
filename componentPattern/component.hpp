
#include <string>

class TheInterface {
public:
    virtual void afn1(int i) = 0;
    virtual int afn2() = 0;
};

class OtherInterface {
public:
    virtual std::string bfn(float f) = 0;
};

class ThirdInterface {
public:
    virtual float cfn(float f) = 0;
};

class MyComponent {
public:
    virtual TheInterface* getTheInterface() = 0;
    virtual OtherInterface* getOtherInterface() = 0;
    virtual ThirdInterface* getThirdInterface() = 0;
    virtual ~MyComponent() { };
    static MyComponent* factory(int n);
};

