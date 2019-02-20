//todo split to .cpp and .h?
//todo rename/merge with py_iterator?
#pragma once
//#define PRINT
#include <Python.h>
#include <exception>
#include <string.h>

#ifdef PRINT
#include <iostream>
#include <cstdio>
using namespace std;
#endif

namespace py_iter{
    template<typename T>
    using converter_to_py = PyObject* (*)(T const &, int&);

    template<typename T, typename BEGIN_TYPE, typename END_TYPE>
    class py_wrapper_iterator {
    public:
        PyObject_HEAD
    private:
        converter_to_py<T> const conv;
        BEGIN_TYPE current;
        END_TYPE const end;
    public:
        py_wrapper_iterator(converter_to_py<T> const conv, BEGIN_TYPE begin, END_TYPE const end) : conv(conv), current(begin), end(end) {}
        static PyObject* next(PyObject *self) {
            auto this_ = reinterpret_cast<py_wrapper_iterator<T, BEGIN_TYPE, END_TYPE> *>(self);

            if (this_->current != this_->end) {
                int ok = true;
                PyObject* ret = nullptr;
                try{
                    ret = this_->conv(*this_->current, ok);
                }
                catch(...) {ok = 0;}
                if (!ok || PyErr_Occurred()) {
                    PyErr_Clear();
                    auto tothrow = PyObject_CallFunction(PyExc_TypeError, "s", "bad element in iterable");
                    throw tothrow;
                }
                ++this_->current;
                return ret;
            }
            PyErr_SetNone(PyExc_StopIteration);
            return nullptr;
        }
        static PyObject* iter(PyObject *self) {
            Py_INCREF(self);
            return self;
        }
        static void free(PyObject *self) {}
        static PyTypeObject typeObject;
    };

    template<typename T, typename BEGIN_TYPE, typename END_TYPE>
    PyTypeObject py_wrapper_iterator<T, BEGIN_TYPE, END_TYPE>::typeObject = {
        PyObject_HEAD_INIT(nullptr)
        "cpp_iterator_adapter", //tp_name;
        sizeof(py_wrapper_iterator<T, BEGIN_TYPE, END_TYPE>), //tp_basicsize
        0, //tp_itemsize

        /* Methods to implement standard operations */

        py_wrapper_iterator<T, BEGIN_TYPE, END_TYPE>::free, //destructor tp_dealloc;
        0, //printfunc tp_print;
        0, //getattrfunc tp_getattr;
        0, //setattrfunc tp_setattr;
        0, //PyAsyncMethods *tp_as_async;
        0, //reprfunc tp_repr;

        /* Method suites for standard classes */

        0, //PyNumberMethods *tp_as_number;
        0, //PySequenceMethods *tp_as_sequence;
        0, //PyMappingMethods *tp_as_mapping;

        /* More standard operations (here for binary compatibility) */

        0, //hashfunc tp_hash;
        0, //ternaryfunc tp_call;
        0, //reprfunc tp_str;
        0, //getattrofunc tp_getattro;
        0, //setattrofunc tp_setattro;

        /* Functions to access object as input/output buffer */
        0, //PyBufferProcs *tp_as_buffer;

        /* Flags to define presence of optional/expanded features */
        Py_TPFLAGS_DEFAULT, //unsigned long tp_flags;

        "A python adapter for a c++ iterable", //const char *tp_doc; /* Documentation string */

        /* call function for all accessible objects */
        0, //traverseproc tp_traverse;

        /* delete references to contained objects */
        0, //inquiry tp_clear;

        /* rich comparisons */
        0, //richcmpfunc tp_richcompare;

        /* weak reference enabler */
        0, //Py_ssize_t tp_weaklistoffset;

        /* Iterators */
        py_wrapper_iterator<T, BEGIN_TYPE, END_TYPE>::iter, //getiterfunc tp_iter;
        py_wrapper_iterator<T, BEGIN_TYPE, END_TYPE>::next, //iternextfunc tp_iternext;

        /* Attribute descriptor and subclassing stuff */
        0, //struct PyMethodDef *tp_methods;
        0, //struct PyMemberDef *tp_members;
        0, //struct PyGetSetDef *tp_getset;
        0, //struct _typeobject *tp_base;
        0, //PyObject *tp_dict;
        0, //descrgetfunc tp_descr_get;
        0, //descrsetfunc tp_descr_set;
        0, //Py_ssize_t tp_dictoffset;
        0, //initproc tp_init;
        0, //allocfunc tp_alloc;
        0, //newfunc tp_new;
        0, //freefunc tp_free; /* Low-level free-memory routine */
        0, //inquiry tp_is_gc; /* For PyObject_IS_GC */
        0, //PyObject *tp_bases;
        0, //PyObject *tp_mro; /* method resolution order */
        0, //PyObject *tp_cache;
        0, //PyObject *tp_subclasses;
        0, //PyObject *tp_weaklist;
        0, //destructor tp_del;

        /* Type attribute cache version tag. Added in version 2.6 */
        0, //unsigned int tp_version_tag;

        0, //destructor tp_finalize;

    };
}


template<typename T, typename ITERABLE_TYPE>
class py_wrapper_iterable {
public:
	PyObject_HEAD
	ITERABLE_TYPE const iterable;
	py_iter::converter_to_py<T> const conv;
private:
public:
	py_wrapper_iterable(): conv(nullptr) {}
	py_wrapper_iterable(py_iter::converter_to_py<T> const conv, ITERABLE_TYPE const iterable) :
	iterable(iterable), conv(conv) {
	}
	static PyObject* iter(PyObject *self) {
		auto this_ = reinterpret_cast<py_wrapper_iterable<T, ITERABLE_TYPE> *>(self);
		using rtype = py_iter::py_wrapper_iterator<T, decltype(this_->iterable.begin()), decltype(this_->iterable.end())>;
		rtype* ret = PyObject_New(rtype, &rtype::typeObject);
		new(ret) rtype(this_->conv, this_->iterable.begin(), this_->iterable.end());
		auto o = reinterpret_cast<PyObject *>(ret);
		return o;
	}
	static void free(PyObject *self) {}
	static PyTypeObject typeObject;
};

template<typename T, typename ITERABLE_TYPE>
PyTypeObject py_wrapper_iterable<T, ITERABLE_TYPE>::typeObject = {
	PyObject_HEAD_INIT(nullptr)
	"cpp_iterable_adapter", //tp_name;
	sizeof(py_wrapper_iterable<T, ITERABLE_TYPE>), //tp_basicsize
	0, //tp_itemsize

	/* Methods to implement standard operations */

	py_wrapper_iterable<T, ITERABLE_TYPE>::free, //destructor tp_dealloc;
	0, //printfunc tp_print;
	0, //getattrfunc tp_getattr;
	0, //setattrfunc tp_setattr;
	0, //PyAsyncMethods *tp_as_async;
	0, //reprfunc tp_repr;

	/* Method suites for standard classes */

	0, //PyNumberMethods *tp_as_number;
	0, //PySequenceMethods *tp_as_sequence;
	0, //PyMappingMethods *tp_as_mapping;

	/* More standard operations (here for binary compatibility) */

	0, //hashfunc tp_hash;
	0, //ternaryfunc tp_call;
	0, //reprfunc tp_str;
	0, //getattrofunc tp_getattro;
	0, //setattrofunc tp_setattro;

	/* Functions to access object as input/output buffer */
	0, //PyBufferProcs *tp_as_buffer;

	/* Flags to define presence of optional/expanded features */
	Py_TPFLAGS_DEFAULT, //unsigned long tp_flags;

	"A python adapter for a c++ iterator", //const char *tp_doc; /* Documentation string */

	/* call function for all accessible objects */
	0, //traverseproc tp_traverse;

	/* delete references to contained objects */
	0, //inquiry tp_clear;

	/* rich comparisons */
	0, //richcmpfunc tp_richcompare;

	/* weak reference enabler */
	0, //Py_ssize_t tp_weaklistoffset;

	/* Iterators */
	py_wrapper_iterable<T, ITERABLE_TYPE>::iter, //getiterfunc tp_iter;
	0, //iternextfunc tp_iternext;

	/* Attribute descriptor and subclassing stuff */
	0, //struct PyMethodDef *tp_methods;
	0, //struct PyMemberDef *tp_members;
	0, //struct PyGetSetDef *tp_getset;
	0, //struct _typeobject *tp_base;
	0, //PyObject *tp_dict;
	0, //descrgetfunc tp_descr_get;
	0, //descrsetfunc tp_descr_set;
	0, //Py_ssize_t tp_dictoffset;
	0, //initproc tp_init;
	0, //allocfunc tp_alloc;
	0, //newfunc tp_new;
	0, //freefunc tp_free; /* Low-level free-memory routine */
	0, //inquiry tp_is_gc; /* For PyObject_IS_GC */
	0, //PyObject *tp_bases;
	0, //PyObject *tp_mro; /* method resolution order */
	0, //PyObject *tp_cache;
	0, //PyObject *tp_subclasses;
	0, //PyObject *tp_weaklist;
	0, //destructor tp_del;

	/* Type attribute cache version tag. Added in version 2.6 */
	0, //unsigned int tp_version_tag;

	0, //destructor tp_finalize;

};
