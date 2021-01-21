#include <vector>
# pragma once

struct Foo{
public:
    virtual int foo0() = 0;
    int foo1();
};

struct Bar{
public:
    virtual int bar0();
    int bar1();
};

struct Baz: public Foo, public Bar{
    int foo0();
    int bar0();
    int baz0();
};