# pragma once

#include "../resources/py_iterable.h"

int sum(py_iterable<int>);
size_t max_len(py_iterable<wchar_t const *>);
struct point{
    int x;
    int y;
};
point agg(py_iterable<point>);
struct person{
    int id;
    int age;
};
int oldest_person_id(py_iterable<person>);
bool any_neg(py_iterable<int> const& _);

double sum_of_products(py_iterable<py_iterable<int>>);