from functools import partial

from swimport.pools.pools import pools
from swimport.pools.types import TypeSwimportingPool
from swimport.pools.derived_types.iter_ import iter_
from swimport.typeswim import TypeSwimporting


@pools.add(TypeSwimportingPool)
def array(inner_type: str, size: int, *, cpp_name='std::array<?,??>', swim, **kwargs):
    """
    as `iter`, but specialized for arrays of a specific size
    :param inner_type: the type to wrap
    :param size: the size pf the array
    :param cpp_name: the cpp type, with ?? replaced with the size
    :param kwargs: additional keyword arguments forwarded to pools.iter
    """
    cpp_name = cpp_name.replace('??', str(size))

    inner_type, inner_porting = swim.get_porting(inner_type)

    port: TypeSwimporting = partial(iter_.get,
                                    (inner_type, inner_porting),
                                    cpp_name=cpp_name, output=list)(swim=swim, insert_func='!!invalid!!', **kwargs)
    if port.to_cpp:
        body = [f"""
                ok = 1;
                auto obj_len = PyObject_Length(input);
                if (obj_len == -1){{
                    if (PyErr_Occurred() != nullptr)
                        SWIM_RAISE_EXISTING;
                }}
                else{{
                    if (obj_len != {size})
                        SWIM_RAISE_TYPE("expected {size} members in: ", input);
                }}
                auto iter = PyObject_GetIter(input);
                if (!iter){{
                    SWIM_RAISE_TYPE("expected an iterable, not ", input);
                }}
                auto temp = PyIter_Next(iter);"""]
        for i in range(size):
            body.append(f"""
            if (!temp)
            {{
                Py_DECREF(iter);
                if (PyErr_Occurred() != nullptr)
                    SWIM_RAISE_EXISTING;
                SWIM_RAISE_TYPE("expected {size} elements, got {i} in: ", input);
            }}
            {inner_type} member_{i} = {inner_porting.to_cpp_func.function_name}(temp, ok, PACKED_UD(0));
            Py_DECREF(temp);
            if (!ok || PyErr_Occurred() != nullptr){{
                Py_DECREF(iter);
                SWIM_RAISE_UNSPECIFIED;
            }}
            temp = PyIter_Next(iter);
            """)
        members = ', '.join(f'member_{i}' for i in range(size))
        body.append(f"""
        Py_DECREF(iter);
        if (temp){{
            Py_DECREF(temp);
            SWIM_RAISE_TYPE("too many elements, expected {size} in: ", input);
        }}
        else if (PyErr_Occurred() != nullptr){{
            SWIM_RAISE_EXISTING;
        }}

        return {{ {members} }};
        """)
        port.to_cpp = port.to_cpp.replace(body='\n'.join(body))
    yield port
