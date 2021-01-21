#include "src.h"

int mutate(int seed, bool inc){
    if (inc)
        return seed+1;
    return seed -1;
}

char* is_ok(bool const* result){
    if (*result)
        return "OK";
    return "ERROR";
}

int sum_of_digits(int seed, int base, bool& IO_overflow){
    auto ret = 0;
    while (seed){
        ret += (seed % base);
        if (!IO_overflow && (ret > base))
            IO_overflow = true;
        seed /= base;
    }
    return ret;
}

int sign(bool b){
    if (b)
        return 1;
    return -1;
}
int sign(int i){
    return sign(i >= 0);
}

bool is_even(int i){
    return i%2 == 0;
}
bool is_even(bool const * b){
    return !*b;
}

int foo(char const* s){
    return 1;
}
int foo(bool b){
    return 2;
}