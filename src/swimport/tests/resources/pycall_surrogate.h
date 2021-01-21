#pragma once
#include <Python.h>
#include <tuple>

//#define PRINT
#ifdef PRINT
#include <iostream>
#include <cstdio>
using namespace std;
#define PY_PRINT(preamble, o) wcout << preamble; PyObject_Print(o, stdout, 0); wcout << endl;
#endif

namespace py_call{
    template <typename T>
    using converter_to_cpp = T (*)(PyObject*, int&);

    template<typename T>
    using converter_to_py = PyObject* (*)(T const &, int&);

    template<typename... ARG_TYPES>
    using converter_to_py_pack = std::tuple<converter_to_py<ARG_TYPES>...>;
}

template<typename RTYPE, typename... ARG_TYPES>
class py_callable{
    const py_call::converter_to_py_pack<ARG_TYPES...> arg_converters;
    const py_call::converter_to_cpp<RTYPE> ret_converter;
    PyObject* const callable;

    template<int dest_index, typename... ARG_TYPES>
    void fill_args(PyObject* sink, ARG_TYPES... args){}

    template<int dest_index, typename FIRST, typename... ARG_TYPES>
    void fill_args(PyObject* sink, FIRST firstarg, ARG_TYPES... args){
        py_call::converter_to_py<FIRST> conv = std::get<dest_index>(arg_converters);
        int ok = 1;
        PyObject* py_arg = nullptr;
        try{
            py_arg = conv(firstarg, ok);
        }
        catch(...) {ok = 0;}
        if (!ok || PyErr_Occurred()){
            throw Py_Ellipsis;
        }
        PyTuple_SET_ITEM(sink, dest_index, py_arg);
        fill_args<dest_index+1, ARG_TYPES...>(sink, args...);
    }
public:
    py_callable(const py_call::converter_to_cpp<RTYPE> ret_converter,
     const py_call::converter_to_py_pack<ARG_TYPES...> arg_converters,
     PyObject* const callable):
    ret_converter(ret_converter), arg_converters(arg_converters), callable(callable){}

    RTYPE call(ARG_TYPES... args){
        #ifdef PRINT
        cout << "called" << endl;
        #endif

        PyObject* py_args = PyTuple_New(sizeof...(ARG_TYPES));
        if (!py_args){
            throw Py_Ellipsis;
        }
        fill_args<0, ARG_TYPES...>(py_args, args...);

        #ifdef PRINT
        PY_PRINT("args: ", py_args);
        cout << "calling inner" << endl;
        #endif

        auto result = PyObject_CallObject(callable, py_args);

        #ifdef PRINT
        PY_PRINT("result: ", result);
        #endif

        Py_DECREF(py_args);

        if (!result){
            throw Py_Ellipsis;
        }

        #ifdef PRINT
        cout << "converting result" << endl;
        #endif

        int ok = 1;
        RTYPE ret = ret_converter(result, ok);

        Py_DECREF(result);

        if (!ok || PyErr_Occurred()){
            throw Py_Ellipsis;
        }

        return ret;
    }
};

template<typename... ARG_TYPES>
class py_callable<void, ARG_TYPES...>{
    const py_call::converter_to_py_pack<ARG_TYPES...> arg_converters;
    PyObject* const callable;

    template<int dest_index, typename... ARG_TYPES>
    void fill_args(PyObject* sink, ARG_TYPES... args){}

    template<int dest_index, typename FIRST, typename... ARG_TYPES>
    void fill_args(PyObject* sink, FIRST firstarg, ARG_TYPES... args){
        PyObject* py_arg;
        py_call::converter_to_py<FIRST> conv = std::get<dest_index>(arg_converters);
        int ok = 1;
        conv(firstarg, &py_arg, ok);
        if (!ok || PyErr_Occurred()){
            throw Py_Ellipsis;
        }
        PyTuple_SET_ITEM(sink, dest_index, py_arg);
        fill_args<dest_index+1, ARG_TYPES...>(sink, args...);
    }
public:
    py_callable(void* sink, const py_call::converter_to_py_pack<ARG_TYPES...> arg_converters,
     PyObject* const callable):
    arg_converters(arg_converters), callable(callable){}

    void call(ARG_TYPES... args){
        PyObject* py_args = PyTuple_New(sizeof...(ARG_TYPES));
        if (!py_args){
            throw Py_Ellipsis;
        }
        fill_args<0, ARG_TYPES...>(py_args, args...);
        auto result = PyObject_CallObject(callable, py_args);
        Py_DECREF(py_args);

        if (!result){
            throw Py_Ellipsis;
        }

        Py_DECREF(result);
    }
};