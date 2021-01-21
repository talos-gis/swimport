# pragma once
# include "../resources/py_slice.h"

bool in_slice(slice<int, int, int> slice, int item);
bool in_continuum(slice<double, double> slice, double item);
slice<double, double> join_continuum(slice<double, double> s1, slice<double, double> s2);
