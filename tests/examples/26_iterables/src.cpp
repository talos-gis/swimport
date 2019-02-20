#include "src.h"

#include <wchar.h>

int sum(py_iterable<int> ints){
    int ret = 0;
    for(int i: ints)
        ret += i;
    return ret;
}
size_t max_len(py_iterable<wchar_t const *> i){
    size_t ret = 0;
    for (auto s:i){
    }

    // show that iterables are re-enterable
    for (wchar_t const * s: i){
        auto len = wcslen(s);
        if (len > ret)
            ret = len;
    }
    return ret;
}
point agg(py_iterable<point> i){
    auto retx = 0, rety = 0;
    for (auto const & p: i){
        retx += p.x;
        rety += p.y;
    }
    return {retx, rety};
}
int oldest_person_id(py_iterable<person> i){
    auto ret = -1;
    auto max = 0;
    for (const person p: i){
        if (p.age > max){
            max = p.age;
            ret = p.id;
        }
    }
    return ret;
}
bool any_neg(py_iterable<int> const & iter){
    for (int i: iter)
        if (i < 0)
            return true;
    return false;
}
double sum_of_products(py_iterable<py_iterable<int>> iter){
    double ret = 0;
    for (auto seq: iter){
        double prod = 1;
        for (auto i: seq){
            prod *= i;
        }
        ret += prod;
    }
    return ret;
}