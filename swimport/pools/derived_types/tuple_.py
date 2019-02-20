from typing import List

from swimport.pools.pools import pools, syspools
from swimport.pools.types import TypeSwimportingPool
from swimport.typeswim import TypeSwimporting, FunctionBody


@syspools.add(TypeSwimportingPool)
def empty_tuple(**type_args):
    return TypeSwimporting('std::tuple<>', 'Tuple[]',
                           to_py="""
                           return PyTuple_New(0);
                           """,
                           to_cpp="""
                           if (!PySequence_Check(input)) {
                                ok = 0;
                                PyErr_SetString(PyExc_TypeError, "expected sequence");
                                return;
                            }
                            if (PySequence_Size(input) != 0) {
                                ok = 0;
                                PyErr_SetString(PyExc_ValueError, "expected exactly 0 items in sequence");
                                return;
                            }
                            ret* = std::make_tuple<>();""",
                           to_cpp_check="""
                           if (!PySequence_Check(input)) {
                                return false;
                            }
                            if (PySequence_Size(input) != 0) {
                                return false;
                            }
                            return true;"""
                           , **type_args)


@pools.add(TypeSwimportingPool, name='tuple')
def tuple_(*types, cpp_name='std::tuple<?>', pair=..., swim, **type_args):
    """
    typemaps for using std::tuple for a set of types
    :param types: the types to handle
    :param cpp_name: the name of the cpp type to map for. ? will be replaced with the type names
    :param pair: whether to also copy the maps for the std::pair type. By default will only apply to pair if the cpp
        name is std::tuple and there are exactly 2 types.
    :param type_args: keyword parameters forwarded to the TypeSwimporting created
    """
    if not types:
        return empty_tuple.get(**type_args)

    sub_portings: List[TypeSwimporting] = []
    types = list(types)
    for i, t in enumerate(types):
        t, sp = swim.get_porting(t)
        types[i] = t
        sub_portings.append(sp)

    cpp_name = cpp_name.replace('?', ', '.join(types))

    to_py_funcs = [sp.to_py_func for sp in sub_portings]
    to_cpp_funcs = [sp.to_cpp_func for sp in sub_portings]
    to_cpp_check_funcs = [sp.to_cpp_check_func for sp in sub_portings]
    to_cpp_post_funcs = [sp.to_cpp_post_func for sp in sub_portings]

    if all(to_py_funcs):
        body = ['ok = 1;',
                f'auto ret = PyTuple_New({len(types)}); if (!ret) {{ok = false; return ret;}};']
        for i, func in enumerate(to_py_funcs):
            body.append(f"""
            {{
                PyObject* _pyval = {func.function_name}(std::get<{i}>(input), ok, PACKED_UD({i}));
                if (!ok || PyErr_Occurred()) {{ return ret; }}
                PyTuple_SET_ITEM(ret, {i}, _pyval);
            }}""")
        body.append("""
            return ret;
            """)

        to_py_func = FunctionBody.combine(*to_py_funcs)(body)
    else:
        to_py_func = None

    if all(to_cpp_funcs):
        body = ['ok = 1;', 'PyObject* _p = nullptr;']
        for i, func in enumerate(to_cpp_funcs):
            body.append(f'{func.owner.cpp_name} _{i};')
        default_tuple = 'std::make_tuple(' + ', '.join(f'_{i}' for i in range(len(to_cpp_funcs))) + ')'
        body.append(
            f"""
            if (!PySequence_Check(input)) {{
                ok = 0;
                PyErr_SetString(PyExc_TypeError, "expected sequence");
                return {default_tuple};
            }}
            if (PySequence_Size(input) != {len(types)}) {{
                ok = 0;
                PyErr_SetString(PyExc_ValueError, "expected exactly {len(types)} items in sequence");
                return {default_tuple};
            }}""")
        for i, func in enumerate(to_cpp_funcs):
            body.append(
                f"""
                _p = PySequence_ITEM(input, {i});
                if (!_p) return {default_tuple};
                _{i} = {func.function_name}(_p, ok, PACKED_UD({i}));
                Py_XDECREF(_p);
                if (!ok || PyErr_Occurred()) return {default_tuple};""")
        body.append(f'return {default_tuple};')

        to_cpp_func = FunctionBody.combine(*to_cpp_funcs)(body)
    else:
        to_cpp_func = None

    if all(to_cpp_check_funcs):
        body = []
        for i, func in enumerate(to_cpp_check_funcs):
            body.append(f'PyObject* _p{i} = nullptr;')
        body.append(f'if (!PyArg_ParseTuple(input, "{"O" * len(types)}", ' + ', '.join(
            '&_p' + str(i) for i in range(len(types))) + f')) return 0;')
        for i, func in enumerate(to_cpp_check_funcs):
            body.append(
                f'if(!{func.function_name}(_p{i}, PACKED_UD({i}))) {{return 0;}}')
        body.append(f'return 1;')

        to_cpp_check_func = FunctionBody.combine(*to_cpp_check_funcs)(body)
    else:
        to_cpp_check_func = None

    if any(to_cpp_post_funcs):
        body = ['ok = 1;']
        for i, func in enumerate(to_cpp_post_funcs):
            if not func:
                continue
            body.append(f'{func.function_name}(std::get<{i}>(input), ok, PACKED_UD({i}));')
        to_cpp_post_func = FunctionBody.combine(*to_cpp_post_funcs)(body)
    else:
        to_cpp_post_func = None

    if pair is ...:
        pair = (cpp_name.startswith('std::tuple<') or cpp_name.startswith('tuple<')) \
               and len(types) == 2
    if pair:
        aliases = ('std::pair<' + ', '.join(types) + '>',)
    else:
        aliases = ()

    return TypeSwimporting(cpp_name, 'Tuple[' + ', '.join(sp.py_name for sp in sub_portings) + ']',
                           to_py=to_py_func,
                           to_cpp=to_cpp_func,
                           to_cpp_check=to_cpp_check_func,
                           to_cpp_post=to_cpp_post_func,
                           aliases=aliases, **type_args)
