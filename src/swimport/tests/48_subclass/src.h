#include <vector>
# pragma once

struct Foo{
    virtual ~Foo();
    virtual bool foo(int x) = 0;
    int bar();
    virtual bool baz(std::vector<int> v) = 0;
    int booz();
    virtual std::vector<int> beer() = 0;
    int boun();
};