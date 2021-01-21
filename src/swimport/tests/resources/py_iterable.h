//todo split to .cpp and .h?
#pragma once
//#define PRINT
#include <Python.h>
#include <exception>

#ifdef PRINT
#include <iostream>
#include <cstdio>
using namespace std;
#endif

namespace py_iter{
    template <typename T>
    using converter_to_cpp = T (*)(PyObject*, int&);
    template <typename T>
    using deleter = void(*)(T const &);

    typedef bool py_iter_term;

    template<typename T>
    class py_iterator {
        PyObject* const iter;
        PyObject* current_py;
        T current_c;
        const converter_to_cpp<T> conv;
        const deleter<T> del_func;

        void advance(){
            #ifdef PRINT
            cout << "advancing: ";
            PyObject_Print(current_py, stdout, 0);
            cout << "->" ;
            #endif

            if ((current_py = PyIter_Next(iter))) {
                #ifdef PRINT
                PyObject_Print(current_py, stdout, 0);
                cout << endl;
                #endif
                int ok = true;
                #ifdef PRINT
                cout << "converting" << endl;
                #endif
                try{
                    current_c = conv(current_py, ok);
                }
                catch(...) {ok = 0;}
                #ifdef PRINT
                cout << "ok= " << ok << endl;
                #endif
                if (!ok || PyErr_Occurred()){
                    PyErr_Clear();
                    auto tothrow = PyObject_CallFunction(PyExc_TypeError, "s", "bad element in iterable");
                    #ifdef PRINT
                    cout << "throwing ";
                    PyObject_Print(tothrow, stdout, 0);
                    cout << endl;
                    #endif
                    throw tothrow;
                }
            }
            #ifdef PRINT
            else{
                cout << "<nothing>" << endl;
            }
            #endif

        }
        void clear_current(){
            if (current_py != nullptr) {
                Py_DECREF(current_py);
                if (del_func)
                    del_func(current_c);
            }
        }
    public:
        py_iterator(PyObject* iter, converter_to_cpp<T> conv, deleter<T> del_func = nullptr) :
        iter(iter), conv(conv), del_func(del_func)
        {
            advance();
        }
        ~py_iterator() {
            clear_current();
            Py_DECREF(iter);
        }
        bool operator!=(py_iter_term const & other) const {
         return current_py != nullptr;
        }
        py_iterator<T>& operator++()
        {
            clear_current();
            advance();

            return *this;
        }
        T const operator*() const{
            return current_c;
        }
        T const * const operator->() const{
            return &current_c;
        }
    };
}

template <typename T>
class py_iterable{
    PyObject* obj;
    py_iter::converter_to_cpp<T> conv;
    py_iter::deleter<T> del_func;
public:
    py_iterable(): py_iterable(nullptr, nullptr, nullptr){};

    py_iterable(PyObject* obj, py_iter::converter_to_cpp<T> conv, py_iter::deleter<T> del_func = nullptr) :
    obj(obj), conv(conv), del_func(del_func) {}

    py_iter::py_iterator<T> begin() const {
        auto iter = PyObject_GetIter(obj);
        return py_iter::py_iterator<T>(iter, conv, del_func);
    }
    const py_iter::py_iter_term end() const {
        return false;
    }

    py_iterable<T>& operator =(const py_iterable<T>& rhs){
        obj = rhs.obj;
        conv = rhs.conv;
        del_func = rhs.del_func;
        return *this;
    }
};