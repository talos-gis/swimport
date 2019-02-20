#include "src.h"
#include <cmath>

PyObject* Point_Create(){
    auto ret = Py_BuildValue("dd",0.0,0.0);
    return ret;
}
double Point_Radius(PyObject* const * p){
    double x,y;
    PyArg_ParseTuple(*p,"dd",&x, &y);
    return std::sqrt(x*x + y*y) ;
}
void Point_Components(PyObject* const& p, PyObject** x, PyObject** y){
    double x_c,y_c;
    PyArg_ParseTuple(p,"dd",&x_c, &y_c);
    *x = Py_BuildValue("dd",x_c,0.0);
    *y = Py_BuildValue("dd",0.0,y_c);
}
void inc(PyObject*& IO_list){
    Py_ssize_t len = PySequence_Size(IO_list);
    for (auto i = 0; i < len; i++){
        PySequence_SetItem(IO_list, i,
            PyNumber_Add(PySequence_GetItem(IO_list, i), PyLong_FromLong(1))
        );
    }
}