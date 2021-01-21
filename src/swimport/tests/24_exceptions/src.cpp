#include "src.h"

#include <stdexcept>
#include <iostream>
#include <fstream>
#include <cerrno>
#include <system_error>
#include <Python.h>

int factorial(int i){
    if (i < 0)
        throw std::invalid_argument("negative value");
    if (!i)
        return 1;
    return factorial(i-1)*i;
}
void* open(){
    throw std::system_error(ENOENT, std::system_category());
    return nullptr;
}
double inv(double d){
    if (d == 0)
        throw std::logic_error("division by zero");
    if (d == -1)
        throw ENOENT;
    if (d == -2)
        throw "-2";
    if (d == -3)
        throw 3.5;
    if (d == -4)
        throw PyObject_CallFunction(PyExc_NameError,"s","waldo");
    if (d == -5)
        throw PyExc_KeyError;
    return 1.0/d;
}
void* copen(){
    errno = ENOENT;
    return nullptr;
}
