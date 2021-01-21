# pragma once
# include <Python.h>

PyObject* Point_Create();
double Point_Radius(PyObject* const * p);
void Point_Components(PyObject* const & p, PyObject** x, PyObject** y);
void inc(PyObject*& IO_list);
