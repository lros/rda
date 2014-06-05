
#include "component.hpp"
#include <iostream>

using namespace std;

int main() {
    MyComponent *component = MyComponent::factory(2);
    TheInterface *theIf = component->getTheInterface();
    OtherInterface *otherIf = component->getOtherInterface();
    ThirdInterface *thirdIf = component->getThirdInterface();
    theIf->afn1(22);
    cout << "The first result is " << theIf->afn2() << endl;
    cout << "The second result is \"" << otherIf->bfn(3.14) << "\"" << endl;
    cout << "The third result is " << thirdIf->cfn(2.718) << endl;
    delete component;
}

