#include "src.h"

int Foo::bar(){
    auto ret = 0;
    for (int i = 0; i < 10; i++){
        if (foo(i))
            ret++;
    }
    return ret;
}
int Foo::booz(){
    std::vector<int> i;
    int ret = 0;
    while (1){
        if (!baz(i)){
            return ret;
        }
        i.push_back(ret);
        ret++;
    }
}
int Foo::boun(){
    auto ret = 0;
    for (int i: beer())
        ret += i;
    return ret;
}
Foo::~Foo(){}
