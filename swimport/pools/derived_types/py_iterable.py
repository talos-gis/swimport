from swimport.pools.pools import pools
from swimport.pools.types import TypeSwimportingPool
from swimport.typeswim import TypeSwimporting, FunctionBody


@pools.add(TypeSwimportingPool)
def input_iterable(inner_type, *, cpp_name='py_iterable<?>', converter_name='py_iter::converter_to_cpp<?>',
                   deleter_name='py_iter::deleter<?>', swim, **type_args):
    """
    typemaps for input iterables
    NOTE: this pool can be applied automatically on most swimported types
    :param inner_type: the type to wrap in iterable input
    :param cpp_name: the name of the type to use in maps.
    :param converter_name: the name of the type of the converter function type.
    :param deleter_name: the name of the type of the deleter function type.
    :param type_args: keyword parameters forwarded to the TypeSwimporting created
    """
    type_args.setdefault('in_iterable_types', ())
    type_args.setdefault('out_iterable_types', ())
    type_args.setdefault('inout_maps', False)

    inner_type, inner_porting = swim.get_porting(inner_type)
    if not inner_porting.to_cpp_func:
        raise Exception(f'type {inner_type} has no to_cpp function')

    cpp_name = cpp_name.replace('?', inner_type)
    converter_name = converter_name.replace('?', inner_type)
    deleter_name = deleter_name.replace('?', inner_type)

    frags = list(inner_porting.to_cpp_func.frags)

    if inner_porting.to_cpp_post_func:
        frags.extend(inner_porting.to_cpp_post_func.frags)

    return TypeSwimporting(cpp_name, py_name=f'Iterable[{inner_porting.py_name}]',
                           to_cpp=FunctionBody(f"""
                                                auto iter = PyObject_GetIter(input);
                                                if (!iter){{
                                                    SWIM_RAISE_TYPE("expected an iterable, not ", input);
                                                }}
                                                Py_DECREF(iter);
                                                return {{input, ({converter_name})PACKED_UD(0), ({deleter_name})PACKED_UD(1)}};
                                               """,
                                               user_data=f"""
                                                void* volatile ud[2];
                                                ud[0] = ({converter_name})([](PyObject* obj, int& ok)
                                                {{
                                                    void* volatile userdata=nullptr;
                                                    {inner_porting.to_cpp_func.user_data}
                                                    return {inner_porting.to_cpp_func.function_name}(obj, ok, userdata);
                                                }});
                                               """
                                                         + (f"""
                                                            ud[1] = ({deleter_name})([] ({inner_type} const & obj)
                                                            {{
                                                            int ok = 1;
                                                            void* volatile userdata=nullptr;
                                                            {inner_porting.to_cpp_post_func.user_data}
                                                            {inner_porting.to_cpp_post_func.function_name}(obj, ok, userdata);
                                                            }});
                                                            """ if inner_porting.to_cpp_post_func else
                                                            """
                                                            ud[1] = nullptr;
                                                            """)
                                                         + """
                                               userdata = (void * volatile)ud; 
                                               """,
                                               fragments=frags),
                           to_cpp_check="""
                                        auto iter = PyObject_GetIter(input);
                                        auto ret = (iter != nullptr);
                                        Py_XDECREF(iter);
                                        PyErr_Clear();
                                        return ret;
                                        """,
                           **type_args)
