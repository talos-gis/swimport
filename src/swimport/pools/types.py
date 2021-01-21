from inspect import signature

from swimport.pools.pools import pools, IdiomaticPool, Pool
from swimport.typeswim import TypeSwimporting, FunctionBody, DefaultCppCheck


class TypeSwimportingPool(Pool):
    """
    A pool that wraps a function returns a TypeSwimporting, or an iterable of TypeSwimportings,
    and automatically applies them to the Swim object.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.swim_param = 'swim' in signature(self.__func__).parameters

    def get(self, *args, **kwargs):
        return self.__func__(*self.args, *args, **self.kwargs, **kwargs)

    def apply(self, swim, args, kwargs):
        if self.swim_param:
            kwargs['swim'] = swim
        ret = self.__func__(*self.args, *args, **kwargs, **self.kwargs)
        return swim(ret)


@pools.add(IdiomaticPool)
def void_ptr(*, swim, **type_args):
    """
    adds the typemaps and functions for void* outputs
    :param type_args: keyword parameters forwarded to the TypeSwimporting created
    """
    type_args.setdefault('inout_maps', False)

    voidptr_swimporting = TypeSwimporting('void*',
                                          to_py=
                                          FunctionBody("""
                                            return SWIG_NewPointerObj(input, (swig_type_info*)userdata, 0|0);
                                          """, user_data="userdata = $descriptor(void*);")
                                          ,
                                          to_cpp="""
                                            void* ptr;
                                            int res;
                                            res = SWIG_ConvertPtr(input,SWIG_as_voidptrptr(&ptr), 0, 0);
                                            if (!SWIG_IsOK(res)) {
                                                PyErr_SetString(PyExc_TypeError, "bad type");
                                                ok = false;
                                                return nullptr;
                                            }
                                            return ptr;
                                          """,
                                          to_cpp_check="""
                                            void* ret;
                                            int res;
                                            res = SWIG_ConvertPtr(input,SWIG_as_voidptrptr(&ret), 0, 0);
                                            if (!SWIG_IsOK(res)) {
                                                return false;
                                            }
                                            return true;
                                          """,
                                          **type_args
                                          )
    swim(voidptr_swimporting)
    swim.add_raw(f'%apply void const * {{void const * INPUT}};')
    swim.add_nl()


@pools.add(IdiomaticPool)
def c_string(swim, **type_args):
    """
    adds the typemaps for c_strings
    :param type_args: keyword parameters forwarded to the TypeSwimporting created
    """
    swim.add_raw('%clear char*;')
    swim.add_raw('%clear char const *;')

    swim(TypeSwimporting('char const *', 'str',
                         to_py="""
                            if (!input){
                                Py_RETURN_NONE;
                            }
                            return PyUnicode_FromString(input);
                            """,
                         to_cpp=FunctionBody("""
                            return (char*)PyUnicode_AsUTF8(input);
                           """),
                         to_cpp_check_precedence="SWIG_TYPECHECK_UNISTRING",
                         **type_args))
    swim(TypeSwimporting('char *', 'str',
                         to_py="""
                            if (!input){
                                Py_RETURN_NONE;
                            }
                            return PyUnicode_FromString(input);
                            """,
                         **type_args))
    swim(TypeSwimporting('wchar_t const *', 'str',
                         to_py="""
                            if (!input){
                                Py_RETURN_NONE;
                            }
                            return PyUnicode_FromWideChar(input, -1);
                            """,
                         to_cpp=FunctionBody("""
                            Py_ssize_t size = 0;
                            return PyUnicode_AsWideCharString(input, &size);
                          """),
                         to_cpp_post="""
                           PyMem_Free((void*)input);
                           """,
                         to_cpp_check_precedence="SWIG_TYPECHECK_STRING",
                         **type_args))
    swim(TypeSwimporting('wchar_t *', 'str',
                         to_py="""
                            if (!input){
                                Py_RETURN_NONE;
                            }
                            return PyUnicode_FromWideChar(input, -1);
                            """,
                         to_cpp="""
                               return PyUnicode_AsWideCharString(input, nullptr);
                              """,
                         to_cpp_post="""
                               PyMem_Free((void*)input);
                               """,
                         to_cpp_check_precedence="SWIG_TYPECHECK_UNISTRING",
                         **type_args))

    to_py = swim.types['char *'].to_py_func

    swim.add_raw(f"""
        %apply char** OUTPUT {{char** OUTPUT_FREE, char*& OUTPUT_FREE, char const ** OUTPUT_FREE, char const *& OUTPUT_FREE}}
        %typemap(argout) char** OUTPUT_FREE, char*& OUTPUT_FREE, char const ** OUTPUT_FREE, char const *& OUTPUT_FREE%{{
            if ($1){{
                int ok = true;
                void* volatile userdata=nullptr;
                {to_py.user_data}
                PyObject* to_add = {to_py.function_name}(*$1, ok, userdata);
                if (!ok || PyErr_Occurred()) SWIG_fail;
                $result = SWIG_Python_AppendOutput($result, to_add);
                delete[] *$1;
            }}
        %}}
        """)

    to_py = swim.types['wchar_t *'].to_py_func
    swim.add_raw(f"""
        %apply wchar_t** OUTPUT {{wchar_t** OUTPUT_FREE, wchar_t*& OUTPUT_FREE, wchar_t const ** OUTPUT_FREE, wchar_t const *& OUTPUT_FREE}}
        %typemap(argout) wchar_t** OUTPUT_FREE, wchar_t*& OUTPUT_FREE, wchar_t const ** OUTPUT_FREE, wchar_t const *& OUTPUT_FREE%{{
            if ($1){{
                int ok = true;
                void* volatile userdata=nullptr;
                {to_py.user_data}
                PyObject* to_add = {to_py.function_name}(*$1, ok, userdata);
                if (!ok || PyErr_Occurred()) SWIG_fail;
                $result = SWIG_Python_AppendOutput($result, to_add);
                delete[] *$1;
            }}
        %}}
        """)

    swim.add_raw("""
        %typemap(newfree) wchar_t*, wchar_t const *, char*, char const*%{
            delete[] $1;
        %}
        """)

    from swimport.functionswim import FunctionBehaviour, ParameterTypeTrigger, ApplyBehaviour, ParameterNameTrigger

    param_rules = (
        (ParameterNameTrigger('SF_.*') & ParameterTypeTrigger(r'(char|wchar_t)( const)? \* [&*]'))
        >> ApplyBehaviour('OUTPUT_FREE'),
        ParameterTypeTrigger(r'(char|wchar_t) const \*') >> ApplyBehaviour('')
    )

    FunctionBehaviour.default_parameters_rules.extendleft(param_rules)


@pools.add(TypeSwimportingPool)
def std_string(**type_args):
    """
    adds the typemaps for std::strings
    :param type_args: keyword parameters forwarded to the TypeSwimporting created
    """
    yield TypeSwimporting('std::string', 'str',
                          to_py="""
                             return PyUnicode_FromString(input.c_str());
                             """,
                          to_cpp="""
                             Py_ssize_t size = 0;
                             auto buffer = PyUnicode_AsUTF8AndSize(input, &size);
                             if (!buffer){
                                SWIM_RAISE_TYPE("expected a string, not ", input);
                             }
                             return {buffer , (size_t)size};
                             """,
                          to_cpp_check_precedence='SWIG_TYPECHECK_STRING',
                          **type_args)

    yield TypeSwimporting('std::wstring', 'str',
                          to_py="""
                            return PyUnicode_FromWideChar(input.c_str(), -1);
                            """,
                          to_cpp="""
                            Py_ssize_t size = 0;
                            auto buffer = PyUnicode_AsWideCharString(input, &size);
                            if (!buffer){
                                ok = false;
                                return {};
                            }
                            std::wstring res(buffer, (size_t)size);
                            PyMem_Free((void*)buffer);
                            return res;
                            """,
                          to_cpp_check_precedence='SWIG_TYPECHECK_UNISTRING',
                          **type_args)


@pools.add(TypeSwimportingPool, name='pyObject')
def py_object(**type_args):
    """
    adds the typemaps to use PyObject* arguments
    :param type_args: keyword parameters forwarded to the TypeSwimporting created
    """
    return TypeSwimporting('PyObject*', 'object',
                           to_py="return input;",
                           to_cpp="return input;",
                           to_cpp_check="return true;",
                           to_cpp_check_precedence=...,
                           ref_maps=TypeSwimporting.REF_MAPS_NO_NONE_CHECK,
                           **type_args)


_prim_maps = [
    ('signed char', 'PyLong_FromLong', 'PyLong_AsLong', 'PyLong_Check', 'SWIG_TYPECHECK_INT8'),
    ('short', 'PyLong_FromLong', 'PyLong_AsLong', 'PyLong_Check', 'SWIG_TYPECHECK_INT16'),
    ('int', 'PyLong_FromLong', 'PyLong_AsLong', 'PyLong_Check', 'SWIG_TYPECHECK_INT32'),
    ('long', 'PyLong_FromLong', 'PyLong_AsLong', 'PyLong_Check', 'SWIG_TYPECHECK_INT64'),
    ('long long', 'PyLong_FromLongLong', 'PyLong_AsLongLong', 'PyLong_Check', 'SWIG_TYPECHECK_INT128'),

    ('unsigned char', 'PyLong_FromUnsignedLong', 'PyLong_AsLong', 'PyLong_Check', 'SWIG_TYPECHECK_UINT8'),
    ('unsigned short', 'PyLong_FromUnsignedLong', 'PyLong_AsLong', 'PyLong_Check', 'SWIG_TYPECHECK_UINT16'),
    ('unsigned int', 'PyLong_FromUnsignedLong', 'PyLong_AsLong', 'PyLong_Check', 'SWIG_TYPECHECK_UINT32'),
    ('unsigned long', 'PyLong_FromUnsignedLong', 'PyLong_AsUnsignedLong', 'PyLong_Check', 'SWIG_TYPECHECK_UINT64'),
    ('unsigned long long', 'PyLong_FromUnsignedLongLong', 'PyLong_AsUnsignedLongLong', 'PyLong_Check',
     'SWIG_TYPECHECK_UINT128'),

    ('size_t', 'PyLong_FromUnsignedLong', 'PyLong_AsUnsignedLong', 'PyLong_Check', 'SWIG_TYPECHECK_UINT64'),

    ('float', 'PyFloat_FromDouble', 'PyFloat_AsDouble', None, 'SWIG_TYPECHECK_FLOAT'),
    ('double', 'PyFloat_FromDouble', 'PyFloat_AsDouble', None, 'SWIG_TYPECHECK_DOUBLE'),
    ('long double', 'PyFloat_FromDouble', 'PyFloat_AsDouble', None, 'SWIG_TYPECHECK_DOUBLE'),
]


@pools.add(IdiomaticPool)
def primitive(*, additionals=True, swim, blacklist=(), **type_args):
    """
    includes typemaps to convert regular c++ primitives as swimport types
    :param additionals: whether to apply typemaps for iterables and sequences of sequences of primitive types
    :param blacklist: primitive types not to import
    :param type_args: keyword parameters forwarded to the TypeSwimporting created
    """
    if isinstance(blacklist, str):
        blacklist = (blacklist,)

    if additionals:
        def additionals(prim):
            iter_types = TypeSwimporting.default_in_iter_types
            for i in iter_types:
                i = i.replace('?', prim)
                swim(pools.input_iterable(i))

            iter_types = TypeSwimporting.default_out_iter_types
            for i in iter_types:
                i = i.replace('?', prim)
                for j in iter_types:
                    swim(pools.iter(i, cpp_name=j))
    else:
        def additionals(x):
            pass

    def import_(port: TypeSwimporting):
        if port.cpp_name in blacklist:
            return
        swim(port)
        additionals(port.cpp_name)

    for prim, topy, tocpp, check, prec in _prim_maps:
        import_(TypeSwimporting(prim,
                                to_py='return ' + topy + '(input);',
                                to_cpp='return ' + tocpp + '(input);',
                                to_cpp_check=('return ' + check + '(input);' if check else DefaultCppCheck()),
                                to_cpp_check_precedence=prec,
                                **type_args))

    import_(TypeSwimporting('char', 'str',
                            to_py="return PyUnicode_FromStringAndSize(&input, 1);",
                            to_cpp="""
                                 Py_ssize_t size = 0;
                                 auto buffer = PyUnicode_AsUTF8AndSize(input, &size);
                                 if (size != 1){
                                    ok = false;
                                    return {};
                                 }
                                 return buffer[0];
                                 """,
                            to_cpp_check_precedence='SWIG_TYPECHECK_CHAR',
                            **type_args))

    import_(TypeSwimporting('wchar_t', 'str',
                            to_py="return PyUnicode_FromWideChar(&input, 1);",
                            to_cpp="""
                                wchar_t buffer[2];
                                 if (PyUnicode_AsWideChar(input, buffer, 2) != 1){
                                    ok = false;
                                    return {};
                                 }
                                 return buffer[0];
                                 """,
                            to_cpp_check_precedence='SWIG_TYPECHECK_UNICHAR',
                            **type_args))

    import_(TypeSwimporting('bool', 'bool',
                            to_py="return PyBool_FromLong(input);",
                            to_cpp="""
                                if (!PyBool_Check(input)){
                                    ok = 0;
                                    return 0;
                                }
                                return (input == Py_True);
                                """,
                            to_cpp_check="return PyBool_Check(input);",
                            to_cpp_check_precedence='SWIG_TYPECHECK_BOOL',
                            **type_args))


@pools.add(TypeSwimportingPool, name='bool')
def bool_(**type_args):
    """
    Allows any python type to be interpreted as a C boolean
    :param type_args: keyword parameters forwarded to the TypeSwimporting created
    """
    return TypeSwimporting('bool', 'Any',
                           to_cpp="""
                                   int res= PyObject_IsTrue(input);
                                   if (res == -1){
                                        ok = 0;
                                        return 0;
                                   }
                                   return res;
                                   """,
                           to_py="""
                               auto ret = input ? Py_True : Py_False;
                               Py_INCREF(ret);
                               return ret;
                               """,
                           to_cpp_check='return 1;',
                           to_cpp_check_precedence=...,
                           ref_maps=TypeSwimporting.REF_MAPS_NO_NONE_CHECK,
                           **type_args)


@pools.add(TypeSwimportingPool)
def singletons(**type_args):
    """
    the necessary typemaps for singleton use
    :param type_args: keyword parameters forwarded to the TypeSwimporting created
    """
    yield TypeSwimporting('ellipsis', 'type(...)',
                          to_py="""
                            Py_INCREF(Py_Ellipsis);
                            return Py_Ellipsis;
                            """,
                          to_cpp="""
                            if (input != Py_Ellipsis){
                                PyErr_SetString(PyExc_TypeError,"expected ellipsis");
                                ok = false;
                                return {};
                            }
                            return Ellipsis;
                            """,
                          to_cpp_check_precedence=0,
                          **type_args
                          )
    yield TypeSwimporting('NoneType', 'type(None)',
                          to_py="""
                            Py_RETURN_NONE;
                            """,
                          to_cpp="""
                            if (input != Py_None){
                                PyErr_SetString(PyExc_TypeError,"expected None");
                                ok = false;
                                return {};
                            }
                            return None;
                            """,
                          to_cpp_check_precedence=0,
                          ref_maps=TypeSwimporting.REF_MAPS_NO_NONE_CHECK,
                          **type_args
                          )
    yield TypeSwimporting('NotImplementedType', 'type(NotImplemented)',
                          to_py="""
                            Py_RETURN_NOTIMPLEMENTED;
                            """,
                          to_cpp="""
                            if (input != Py_NotImplemented){
                                PyErr_SetString(PyExc_TypeError,"expected NotImplemented");
                                ok = false;
                                return {};
                            }
                            return NotImplemented;
                            """,
                          to_cpp_check_precedence=0,
                          **type_args
                          )
    yield TypeSwimporting('PySingleton',
                          to_py="""
                            if (input == None)
                                Py_RETURN_NONE;
                            else if (input == NotImplemented)
                                Py_RETURN_NOTIMPLEMENTED;
                            else if (input == Ellipsis)
                            {
                                Py_INCREF(Py_Ellipsis);
                                return Py_Ellipsis;
                            }
                            ok = 0;
                            Py_RETURN_NONE;
                            """,
                          to_cpp="""
                            if (input == Py_NotImplemented)
                                return NotImplemented;
                            if (input == Py_None)
                                return None;
                            if (input == Py_Ellipsis)
                                return Ellipsis;
                            PyErr_SetString(PyExc_TypeError,"expected a singleton type"); 
                            ok = false;
                            return {};
                            """,
                          to_cpp_check_precedence=0,
                          ref_maps=TypeSwimporting.REF_MAPS_NO_NONE_CHECK,
                          **type_args
                          )


@pools.add(TypeSwimportingPool, name='complex')
def complex_(**type_args):
    """
    typemaps for using std::complex<double> and std::complex<float>
    :param type_args: keyword parameters forwarded to the TypeSwimporting created
    """
    yield TypeSwimporting('std::complex<double>', 'complex',
                          to_py="""
                                return PyComplex_FromDoubles(std::real(input), std::imag(input));
                                """,
                          to_cpp="""
                                if (PyComplex_Check(input)){
                                    return {PyComplex_RealAsDouble(input), PyComplex_ImagAsDouble(input)};
                                }
                                if (PyNumber_Check(input)){
                                    auto f = PyNumber_Float(input);
                                    auto result = PyFloat_AS_DOUBLE(f);
                                    Py_DECREF(f);
                                    return result;
                                }
                                PyErr_SetString(PyExc_TypeError, "expected a number");
                                ok = 0;
                                """,
                          to_cpp_check_precedence="SWIG_TYPECHECK_COMPLEX",
                          **type_args)
    yield TypeSwimporting('std::complex<float>', 'complex',
                          to_py="""
                                return PyComplex_FromDoubles(std::real(input), std::imag(input));
                                """,
                          to_cpp="""
                                if (PyComplex_Check(input)){
                                    return {(float)PyComplex_RealAsDouble(input), (float)PyComplex_ImagAsDouble(input)};
                                }
                                if (PyNumber_Check(input)){
                                    auto f = PyNumber_Float(input);
                                    auto result = (float)PyFloat_AS_DOUBLE(f);
                                    Py_DECREF(f);
                                    return result;
                                }
                                PyErr_SetString(PyExc_TypeError, "expected a number");
                                ok = 0;
                                """,
                          to_cpp_check_precedence="SWIG_TYPECHECK_COMPLEX",
                          **type_args)
