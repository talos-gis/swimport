from swimport.pools.pools import pools
from swimport.pools.types import TypeSwimportingPool
from swimport.typeswim import TypeSwimporting, FunctionBody


@pools.add(TypeSwimportingPool, name='iter')
def iter_(inner_type, *, cpp_name='std::vector<?>', input_=..., insert_func=..., reserve=..., output=iter, swim,
          **type_args):
    """
    typemaps for iterable type
    :param inner_type: the type to wrap in iterable input
    :param cpp_name: the name of the type to use in maps.
    :param input_: whether to include input typemaps for the type. ... is to only include if available.
    :param insert_func: the name of the function to insert values into the cpp type. Default is to guess based on
        cpp_name. Only used if input is true.
    :param reserve: whether to call reserve on the C++ structure using an input's __length_hint__. Default is
        to only reserve for std::vector. Only used if input is true.
    :param output: whether to include output typemaps for the type. False, for nothing.
        Default is to use an iterable adapter.
    :param type_args: keyword parameters forwarded to the TypeSwimporting created
    """
    type_args.setdefault('in_iterable_types', ())
    type_args.setdefault('out_iterable_types', ())
    type_args.setdefault('inout_maps', False)

    inner_type, inner_porting = swim.get_porting(inner_type)

    cpp_name = cpp_name.replace('?', inner_type)

    if not inner_porting.to_cpp_func:
        if input_ is True:
            raise Exception(f'type {inner_type} has no to_cpp function')
        elif input_ is ...:
            input_ = False
    elif input_ is ...:
        input_ = True

    if not inner_porting.to_py_func:
        if output is True:
            raise Exception(f'type {inner_type} has no to_py function')
        elif output is ...:
            output = False
    elif output is ...:
        output = True

    if output is iter:
        iterable_type = 'py_wrapper_iterable<' + inner_type + ', ' + cpp_name + '>'
        converter_name = 'py_iter::converter_to_py<?>'.replace('?', inner_type)
        to_py = FunctionBody(f"""
                    using rtype = {iterable_type};
                    rtype* a = PyObject_New(rtype, &rtype::typeObject);
                    new(a) rtype(({converter_name})userdata, input);
                    return (PyObject*)a;
                   """,
                             user_data=f"""userdata = ({converter_name})([]({inner_type} const & v, int& ok)
                                            {{
                                                void* volatile userdata=nullptr;
                                                {inner_porting.to_py_func.user_data}
                                                return {inner_porting.to_py_func.function_name}(v, ok, userdata);
                                            }});
                                           """,
                             fragments=inner_porting.to_py_func.frags)
    elif output is list:
        to_py = FunctionBody.combine(inner_porting.to_py_func)(f"""
            ok = 1;
            auto ret = PyList_New(input.size());
            if (!ret){{
                ok = 0;
                return nullptr; 
            }}
            Py_ssize_t  i = 0;
            for (auto e: input){{
                PyObject* to_add = {inner_porting.to_py_func.function_name}(e, ok, PACKED_UD(0));
                if (!ok || PyErr_Occurred()){{
                    Py_CLEAR(ret);
                    return nullptr;
                }}             
                PyList_SET_ITEM(ret, i, to_add); 
                if (!ok || PyErr_Occurred()){{
                    Py_XDECREF(ret);
                    return nullptr;
                }}
                i++;
            }}
            return ret;
        """)
    elif output is tuple:
        to_py = FunctionBody.combine(inner_porting.to_py_func)(f"""
                ok = 1;
                auto ret = PyTuple_New(input.size());
                if (!ret){{
                    ok = 0;
                    return nullptr; 
                }}
                Py_ssize_t  i = 0;
                for (auto e: input){{
                    PyObject* to_add = {inner_porting.to_py_func.function_name}(e, ok, PACKED_UD(0));
                    if (!ok || PyErr_Occurred()){{
                        Py_CLEAR(ret);
                        return nullptr;
                    }}                
                    PyTuple_SET_ITEM(ret, i, to_add); 
                    i++;
                }}
                return ret;
                """)
    elif output is set:
        to_py = FunctionBody.combine(inner_porting.to_py_func)(f"""
                ok = 1;
                auto ret = PySet_New(nullptr);
                if (!ret){{
                    ok = 0;
                    return nullptr; 
                }}
                for (auto e: input){{
                    auto to_add = {inner_porting.to_py_func.function_name}(e, ok, PACKED_UD(0));
                    if (!ok || PyErr_Occurred()){{
                        SWIM_THROW_UNSPECIFIED;
                    }}                
                    if (PySet_Add(ret, to_add)){{
                        Py_DECREF(to_add);
                        SWIM_THROW_UNSPECIFIED;
                    }} 
                }}
                return ret;
                """)
    elif output is frozenset:
        to_py = FunctionBody.combine(inner_porting.to_py_func)(f"""
                ok = 1;
                auto ret = PyFrozenSet_New(nullptr);
                if (!ret){{
                    ok = 0;
                    return nullptr; 
                }}
                for (auto e: input){{
                    auto to_add = {inner_porting.to_py_func.function_name}(e, ok, PACKED_UD(0));
                    if (!ok || PyErr_Occurred()){{
                        SWIM_THROW_UNSPECIFIED;
                    }}                
                    if (PySet_Add(ret, to_add)){{
                        Py_DECREF(to_add);
                        SWIM_THROW_UNSPECIFIED;
                    }} 
                }}
                return ret;
                """)
    elif not output:
        to_py = None
    else:
        raise TypeError('bad type for output')

    if input_:
        if insert_func is ...:
            if any((cpp_name.startswith(prefix) or cpp_name.startswith('std::' + prefix))
                   for prefix in ('vector<', 'deque<', 'list<', 'forward_list<')):
                insert_func = 'push_back'
            elif any((cpp_name.startswith(prefix) or cpp_name.startswith('std::' + prefix))
                     for prefix in ('unordered_set<', 'set<')):
                insert_func = 'insert'
            else:
                raise Exception('could not guess insert_func for type ' + cpp_name)

        if reserve is ...:
            reserve = any(
                cpp_name.startswith(pref) for pref in ('std::vector<', 'vector<')
            )

        to_cpp = FunctionBody.combine(inner_porting.to_cpp_func)(
            f"""
            ok = 1;
            auto iter = PyObject_GetIter(input);
            if (!iter){{
                SWIM_RAISE_TYPE("expected an iterable, not ", input);
            }}
            {cpp_name} ret;
            """
            +
            ("""
                auto size = PyObject_LengthHint(input, -2);
                if (size >= 0)
                    ret.reserve(size);
                else if (size != -2){
                    SWIM_RAISE_EXISTING;
                }
            """ if reserve else "")
            +
            f"""                
            PyObject* current;
            while(current = PyIter_Next(iter)){{
                {inner_type} cpp_curr = {inner_porting.to_cpp_func.function_name}(current, ok, PACKED_UD(0));
                Py_DECREF(current);
                if (!ok || PyErr_Occurred()){{
                    PyErr_SetString(PyExc_TypeError, "could not convert object in iterable"); 
                    SWIM_RAISE_UNSPECIFIED;
                }}
                ret.{insert_func}(cpp_curr);
            }}
            Py_DECREF(iter);
            return ret;
            """)

        to_cpp_check = """
                    auto iter = PyObject_GetIter(input);
                    auto ret = (iter != nullptr);
                    Py_XDECREF(iter);
                    PyErr_Clear();
                    return ret;
                    """

        if inner_porting.to_cpp_post_func:
            to_cpp_post = FunctionBody.combine(inner_porting.to_cpp_post_func)(f"""
            for (auto e: input){{
                {inner_porting.to_cpp_post_func.function_name}(e, ok, PACKED_UD(0));
                if (!ok || PyErr_Occurred())
                    return;
            }}
            """)
        else:
            to_cpp_post = None

    else:
        to_cpp = None
        to_cpp_check = None
        to_cpp_post = None

    return TypeSwimporting(cpp_name, 'Iterable[' + inner_porting.py_name + ']',
                           to_py=to_py,
                           to_cpp=to_cpp,
                           to_cpp_check=to_cpp_check,
                           to_cpp_post=to_cpp_post,
                           **type_args)


set_ = pools.add(..., name='set', doc='as `iter`, but specialized for sets')(
    iter_(cpp_name='std::unordered_set<?>', output=set))

frozenset_ = pools.add(..., name='frozenset', doc='as `iter`, but specialized for frozensets')(
    iter_(cpp_name='std::unordered_set<?>', output=frozenset))

list_ = pools.add(..., name='list', doc='as `iter`, but specialized for lists')(
    iter_(cpp_name='std::vector<?>', output=list))

