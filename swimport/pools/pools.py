from typing import Dict, Union, Callable, Iterable

from abc import ABC

from textwrap import dedent
from datetime import datetime
from functools import partial

from swimport.model import FileSource
import swimport_data as data
import swimport.swim as swim_module


class Pool(ABC):
    """a class for pools or pools with partial arguments"""

    def __init__(self, func: Callable, name, args, kwargs):
        super().__init__()
        self.__func__ = func
        self.args = args
        self.kwargs = kwargs
        self.name = name
        self._doc = None

    def apply(self, swim, args, kwargs):
        ret = self.__func__(*self.args, *args, swim=swim, **kwargs, **self.kwargs)
        if ret is None:
            ret = True
        return ret

    def __call__(self, *args, **kwargs):
        if not (args or kwargs):
            return self
        if args and isinstance(args[-1], swim_module.Swim):
            *args, swim = args
            return self.apply(swim, args, kwargs)
        elif 'swim' in kwargs:
            swim = kwargs.pop('swim')
            return self.apply(swim, args, kwargs)
        else:
            args = self.args + args
            kwargs = {**self.kwargs, **kwargs}
            return type(self)(self.__func__, self.name, args, kwargs)

    @property
    def func(self):
        return partial(self.__func__, *self.args, **self.kwargs)

    @property
    def __doc__(self):
        return self._doc

    @__doc__.setter
    def __doc__(self, v):
        if v is None:
            self._doc = None
        else:
            self._doc = self.name + ':\n\t' + '\n\t'.join(dedent(v).strip().splitlines(keepends=False))

    def __hash__(self):
        return hash((type(self), self.__func__, self.args, tuple(self.kwargs.items())))

    def __eq__(self, other):
        return type(self) == type(other) \
               and (self.__func__, self.args, self.kwargs, self.kwargs) == \
               (other.__func__, other.args, other.kwargs, other.kwargs)

    def __str__(self):
        return 'pool: ' + self.name


class IdiomaticPool(Pool):
    """
    A pool that checks that it hasn't been used before
    """

    def apply(self, swim, args, kwargs):
        if self in swim.imported:
            return False
        ret = super().apply(swim, args, kwargs)
        swim.imported[self] = self
        return ret

    @property
    def __doc__(self):
        return Pool.__doc__.fget(self)

    @__doc__.setter
    def __doc__(self, v):
        Pool.__doc__.fset(self, v)


class Pools(Iterable[Pool]):
    """
    Class for object containing all the pools.
    """

    def __init__(self):
        self.registry: Dict[str, Pool] = {}

    def __contains__(self, item):
        return item in self.registry

    def __iter__(self):
        yield from self.registry.values()

    def __len__(self):
        return len(self.registry)

    def add(self, pool_cls=Pool, **kwargs):
        def ret(func, name=..., doc=...):
            nonlocal pool_cls
            if name is ...:
                name = func.__name__
            if doc is ...:
                doc = func.__doc__
            if pool_cls is ...:
                pool_cls = type(func)
                func = func.func

            to_register = pool_cls(func, name, (), {})
            to_register.__doc__ = doc

            v = self.registry.setdefault(name, to_register)
            setattr(self, name, to_register)
            if v is not to_register:
                raise Exception('duplicate pool name: ' + name)
            return to_register

        return partial(ret, **kwargs)


class DocumentingPools(Pools):
    """
    A pools object that updates its __doc__ when a pool is added to it.
    """

    def __init__(self, preamble: str = ''):
        super().__init__()
        self.auto_build_doc = True  # set this to false before adding a lot of pools, then set it to true again.
        self.__doc__ = ''
        self.preamble = preamble

    def add(self, *args, **kwargs):
        ret_ = super().add(*args, **kwargs)

        def ret(*args, **kwargs):
            r = ret_(*args, **kwargs)
            if self.auto_build_doc:
                self.rebuild_doc()
            return r

        return ret

    def rebuild_doc(self):
        self.__doc__ = self.preamble + '\n\n'.join(p.__doc__ for p in sorted(self, key=lambda p: p.name))


pools = DocumentingPools('The following pools are available:\n\n')
pools.auto_build_doc = False

syspools = Pools()  # contains pools that are meant to pe added programmatically, not manually


@pools.add(IdiomaticPool)
def disclose(swim):
    """
    add a disclosure the file was generated, including the swimport version and the time
    """
    swim.add_comment_ml(f"""
                    This file was programmatically generated with {data.__name__} v{data.__version__}
                    on {datetime.now():%Y-%m-%d %H:%M}
                    """)
    swim.add_nl()


@syspools.add(IdiomaticPool)
def std_exception(swim):
    swim(include("<exception>", "<system_error>", "<stdexcept>", "<typeinfo>", "<utility>"))
    swim.add_begin("""
    #define SWIM_STD_CATCH(ctype, ptype) catch (const ctype& e){PyErr_SetString(ptype, e.what()); SWIG_fail;}
""")

    swim.add_raw("""
%define SWIM_STD_EXCEPTION(pattern)
%exception{
    try {
        $action;
    }
    catch (PyObject* const & e){
        if (e == nullptr)
        {
            PyErr_SetString(PyExc_Exception, "an null of static type python object was thrown");
            SWIG_fail;
        }
        if (e == Py_Ellipsis)
        {
            //raising ... means we have an exception ready, just fail without setting an error
            SWIG_fail;
        }
        if (PyObject_IsInstance(e, PyExc_BaseException))
        {
            PyObject* type = PyObject_Type(e);
            PyObject* args = PyObject_GetAttrString(e, "args");
            PyErr_SetObject(type, args);
            Py_DECREF(type);
            Py_DECREF(args);
            Py_DECREF(e);
            SWIG_fail;
        }
        if (PyObject_IsSubclass(e, PyExc_BaseException) == 1)
        {
            PyErr_SetNone(e);
            Py_DECREF(args);
            SWIG_fail;
        }
        PyObject* args = Py_BuildValue("(sN)", "a non-exception python object was thrown", e);
        PyErr_SetObject(PyExc_Exception, args);
        Py_DECREF(args);
        SWIG_fail;
    }
    catch(std::pair<PyObject*, std::string> const & p){
        std::string msg = "error while running function $symname: ";
        msg += std::get<1>(p);
        PyErr_SetString(std::get<0>(p), msg.c_str()); SWIG_fail;
    }
    catch (const std::system_error& e){            
        PyObject* args = Py_BuildValue("(is)", e.code(), e.what());
        PyErr_SetObject(PyExc_OSError, args);
        Py_DECREF(args);
        SWIG_fail;
    }
    catch (const char*& e){
        PyErr_SetString(PyExc_Exception, e);
        SWIG_fail;
    }
    catch (const int& e){
    #if !defined(_WIN32) && (defined(__unix__) || defined(__unix) || (defined(__APPLE__) && defined(__MACH__)))
        PyObject* args = Py_BuildValue("i", e);
        PyErr_SetObject(PyExc_OSError, args);
        Py_DECREF(args);
    #else
        PyErr_SetFromWindowsErr(e);
    #endif
        SWIG_fail;
    }
    SWIM_STD_CATCH(std::bad_alloc, PyExc_MemoryError)
    SWIM_STD_CATCH(std::bad_cast, PyExc_TypeError)
    SWIM_STD_CATCH(std::bad_typeid, PyExc_TypeError)
    SWIM_STD_CATCH(std::range_error, PyExc_OverflowError)
    SWIM_STD_CATCH(std::overflow_error, PyExc_OverflowError)
    SWIM_STD_CATCH(std::underflow_error, PyExc_OverflowError)
    SWIM_STD_CATCH(std::logic_error, PyExc_ValueError)
    SWIM_STD_CATCH(std::exception, PyExc_Exception)
    catch(...){
        PyErr_SetString(PyExc_Exception, "an non-exception was thrown");
        SWIG_fail;
    }
    
    if (errno){
    #if !defined(_WIN32) && (defined(__unix__) || defined(__unix) || (defined(__APPLE__) && defined(__MACH__)))
        PyErr_SetFromErrno(PyExc_OSError);
    #else
        PyErr_SetFromWindowsErr(errno);
    #endif
        SWIG_fail;
    }
}
%enddef
""")


@pools.add(IdiomaticPool, name='print')
def print_(swim):
    """
    adds the neccessary lines to print (using cout) in the code.
    """
    swim.add_begin("""
                #include <iostream>
                #include <cstdio>
                #define PY_PRINT(preamble, o) wcout << preamble; PyObject_Print(o, stdout, 0); wcout << endl;
                using namespace std;
                """)
    swim.add_nl()


@syspools.add(IdiomaticPool)
def dll_main(swim):
    swim.add_begin('''
            #include <windows.h>
            #include <iostream>
            #define SWIM_LOAD_HANDLE(name) HINSTANCE SWIM_DLL_HANDLE_##name = LoadLibrary(#name ".dll");if(!SWIM_DLL_HANDLE_##name){PyErr_SetString(PyExc_ImportError, "could not load library " #name);return NULL;}
            #define SWIM_DECL_IMPORTED_FUNC(retType,name,...) typedef retType (*SWIM_FUNC_TYPE_##name)(__VA_ARGS__); SWIM_FUNC_TYPE_##name SWIM_FUNC_HANDLE_##name;
            #define SWIM_IMPORT_FROMDLL(func,handleName) SWIM_FUNC_HANDLE_##func = (SWIM_FUNC_TYPE_##func)GetProcAddress(SWIM_DLL_HANDLE_##handleName, #func); if (!SWIM_FUNC_HANDLE_##func){PyErr_SetString(PyExc_ImportError, "could not load function " #func " from " #handleName ".dll"); return NULL;}
        ''')


@syspools.add(IdiomaticPool)
def dll_load(name, *, swim):
    if name.endswith('.dll'):
        name = name[:-len('.dll')]
    swim.add_init(f'SWIM_LOAD_HANDLE({name})')


@pools.add(Pool)
def dlls(*dll_names, swim):
    """
    if you want to import functions from dlls.
    :param dll_names: an optional list of dll names to load.
    """
    swim(dll_main())
    for name in dll_names:
        swim(dll_load(name))
    swim.add_nl()


@pools.add(Pool)
def module(name, docstring=None, package=None, *, swim, **kwargs):
    """
    to specify the module name (if the swim is initialized with a name, this is called automatically)
    :param name: the name of the output module
    :param docstring: the docstring of the module, if any
    :param package: the package of the module, if any
    :param kwargs: additional options for the module
    """
    options = kwargs
    if docstring:
        options['docstring'] = '"' + docstring + '"'
    if package:
        options['package'] = '"' + package + '"'
    if options:
        opt_string = '(' + ', '.join(k + ' = ' + v for k, v in options.items()) + ')'
    else:
        opt_string = ''
    swim.add_raw('%module' + opt_string + ' ' + name)
    swim.add_nl()


@pools.add(IdiomaticPool)
def include(*sources: Union[FileSource, str], swim):
    """
    include a source with its preprocessor directives
    :param sources: the source objects or paths to cpp header files
    """
    lines = []
    for source in sources:
        if isinstance(source, str):
            if source.startswith('<') or source.startswith('"'):
                lines.append('#include ' + source)
                continue
            source = FileSource(source)
        lines.extend('#define ' + directive for directive in source.directives)
        lines.append('#include "' + source.source_path + '"')
        lines.extend('#undef ' + directive for directive in reversed(source.directives))

    swim.add_begin(lines)
    swim.add_nl()


@syspools.add(IdiomaticPool)
def ns_trap_main(swim):
    swim.add_python_begin("""
                    class _SWIMPORT_NamespaceTrap:
                        # an object that, when overridden, deletes its overrider from the namespace
                        def __init__(self, ns, key):
                            self.ns = ns
                            self.key = key
                        def __del__(self):
                            self.ns.pop(self.key, None)
                    """)


@syspools.add(IdiomaticPool)
def ns_trap_name(name, *, swim):
    swim.add_python(f"""
                try:
                    del {name}
                except NameError:
                    {name} = _SWIMPORT_NamespaceTrap(globals(), '''{name}''')
                """)


@syspools.add(IdiomaticPool)
def ns_trap(*names, swim):
    """
    include a python class to delete whatever overrides it in the namespace
    """
    swim(ns_trap_main())
    for name in names:
        swim(ns_trap_name(name))


@syspools.add(IdiomaticPool)
def typemap_macros(swim):
    swim(include("<exception>", "<utility>", "<string>"))
    swim.add_begin("""
    #define PACKED_UD(ind) (((void**)userdata)[(ind)])
    // note: RAISE macros are supposed to be thrown form py->cpp functions, and THROW from cpp->py
    #define SWIM_RAISE(TYPE,MSG) throw std::pair<PyObject*, std::string>((TYPE), (MSG))
    #define SWIM_RAISE_KEY(MSG, KEY)   { std::string msg = (MSG);\\
                                         auto key_str = PyObject_Str((KEY));\\
                                         msg += PyUnicode_AsUTF8(key_str);\\
                                         Py_DECREF(key_str);\\
                                         SWIM_RAISE(PyExc_KeyError, msg); }
    #define SWIM_RAISE_TYPE(MSG, OBJ)  { std::string msg = (MSG);\\
                                         auto otype = PyObject_Type((OBJ)); \\
                                         auto otype_str = PyObject_Str(otype);\\
                                         msg += PyUnicode_AsUTF8(otype_str);\\
                                         Py_DECREF(otype);\\
                                         Py_DECREF(otype_str);\\
                                         SWIM_RAISE(PyExc_TypeError, msg); }
    #define SWIM_RAISE_UNSPECIFIED_VAR(var) SWIM_RAISE_TYPE("an unspecified exception occurred, input type: ", var);
    #define SWIM_RAISE_UNSPECIFIED SWIM_RAISE_UNSPECIFIED_VAR(input);
    #define SWIM_RAISE_EXISTING throw Py_Ellipsis;
    
    #define SWIM_THROW SWIM_RAISE
    #define SWIM_THROW_TYPE(MSG, OBJ)  { std::string msg = (MSG);\\
                                         msg += typeid((OBJ)).name();\\
                                         SWIM_RAISE(PyExc_TypeError, msg); }
    #define SWIM_THROW_UNSPECIFIED_VAR(var) SWIM_THROW_TYPE("an unspecified exception occurred, input type: ", var);
    #define SWIM_THROW_UNSPECIFIED SWIM_THROW_UNSPECIFIED_VAR(input);
    #define SWIM_THROW_EXISTING SWIM_RAISE_EXISTING
    """)
