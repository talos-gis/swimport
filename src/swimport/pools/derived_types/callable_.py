from typing import List

from itertools import chain
from warnings import warn

from swimport.pools.pools import pools
from swimport.pools.types import TypeSwimportingPool
from swimport.typeswim import TypeSwimporting, FunctionBody


@pools.add(TypeSwimportingPool, name='callable')
def callable_(ret_type, *arg_types, cpp_name='std::function<?>', surrogate_type_name='py_callable<?>',
              on_ret_post='raise', swim,
              **type_args):
    """
    typemaps for using std::function for a set of types
    :param ret_type: the return type of the function, or void (or None)
    :param arg_types: the types of the arguments
    :param cpp_name: the name of the cpp type to map for. ? will be replaced with the type names
    :param surrogate_type_name: the type name of the surrogate object to adapt between a python callable and
        a c++ object.
    :param on_ret_post: What to do if the return type has a to_cpp_post map, 'raise', 'warn', or None.
    :param type_args: keyword parameters forwarded to the TypeSwimporting created
    """
    arg_portings: List[TypeSwimporting] = []
    if ret_type == 'void':
        ret_type = None

    if ret_type:
        ret_type, ret_porting = swim.get_porting(ret_type)
        if not ret_porting.to_cpp_func:
            raise ValueError('the return type ' + ret_type + ' does not have a to_cpp function')
        if ret_porting.to_cpp_post_func:
            msg = f"the return type {ret_type} has a to_cpp_post function, that the object will not be able to"\
                    f" dispose of, memory leaks possible"
            if on_ret_post == 'warn':
                warn(msg)
            elif on_ret_post is None:
                pass
            else:
                raise ValueError(msg)
    else:
        ret_type = 'void'
        ret_porting = None

    arg_types = list(arg_types)
    for i, t in enumerate(arg_types):
        t, sp = swim.get_porting(t)
        if not sp.to_py_func:
            raise ValueError('the type ' + t + ' does not have a to_py function')
        arg_portings.append(sp)
        arg_types[i] = t

    cpp_name = cpp_name.replace('?', ret_type + '(' + ', '.join(arg_types) + ')')
    surrogate_type_name = surrogate_type_name.replace('?', ', '.join(chain((ret_type,), arg_types)))

    swim(pools.include("<tuple>"))

    to_cpp_body = [
        f"""
        if (!PyCallable_Check(input)){{
            PyErr_SetString(PyExc_TypeError, "expected a callable object");
            return {{}};
        }}
        auto to_py_conv_pack = std::make_tuple({','.join(
            "(py_call::converter_to_py<" + t + ">)PACKED_UD(" + str(i) + ")" for i, t in enumerate(arg_types))});
        """
    ]
    if ret_porting:
        to_cpp_body.append(
            f"auto to_cpp_conv = (py_call::converter_to_cpp<{ret_type}>)PACKED_UD({len(arg_types)});"
        )
    else:
        to_cpp_body.append(
            f"void* to_cpp_conv = nullptr;"
        )
    to_cpp_body.append(
        f"""
        {surrogate_type_name} surrogate(to_cpp_conv, to_py_conv_pack, input);
        return ({cpp_name})std::bind( std::mem_fn(&{surrogate_type_name}::call) , {", ".join(
            chain(("surrogate",), ('std::placeholders::_' + str(i) for i, _ in enumerate(arg_types, 1))))});
        """
    )
    if not (arg_portings or ret_porting):
        userdata = ''
        frags = ()
    else:
        userdata = [f'void* volatile ud[{len(arg_portings) + bool(ret_porting)}] = {{}};']
        frags = []
        for i, sp in enumerate(arg_portings):
            fb = sp.to_py
            t = sp.cpp_name
            userdata.append(f"""
            {{
                ud[{i}] = (py_call::converter_to_py<{t}>)[]({t} const & input,int& ok){{ 
                    void* volatile userdata=nullptr;  // userdata for type {t}
                    {{
                    {fb.user_data}
                    }}
                    return {fb.function_name}(input, ok, userdata);
                }};
            }}
            """)
            frags.extend(fb.frags)
        if ret_porting:
            fb = ret_porting.to_cpp
            t = ret_type
            userdata.append(f"""
            {{
                ud[{len(arg_portings)}] = (py_call::converter_to_cpp<{t}>)[](PyObject* input,int& ok){{ 
                    void* volatile userdata=nullptr;  // userdata for type {t}
                    {{
                    {fb.user_data}
                    }}
                    return {fb.function_name}(input, ok, userdata);
                }};
            }}
            """)
            frags.extend(fb.frags)

        userdata.append('userdata = (void* volatile)ud;')
        userdata = '\n'.join(userdata)

    to_cpp = FunctionBody(to_cpp_body, user_data=userdata, fragments=frags)

    return TypeSwimporting(cpp_name, py_name='Callable',
                           to_cpp=to_cpp,
                           to_cpp_check='return PyCallable_Check(input);',
                           **type_args)