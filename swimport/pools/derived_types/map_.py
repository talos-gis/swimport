from swimport.pools.pools import pools
from swimport.pools.types import TypeSwimportingPool
from swimport.pools.derived_types.iter_ import iter_
from swimport.typeswim import TypeSwimporting, FunctionBody


@pools.add(TypeSwimportingPool, name='map')
def map_(key_type, value_type, *, cpp_name='std::unordered_map<?>', output=dict, swim, **type_args):
    """
    typemaps for using std::tuple for a set of types
    :param key_type: the key type to handle
    :param value_type: the value type to handle
    :param cpp_name: the name of the cpp type to map for. ? will be replaced with the type names
    :param type_args: keyword parameters forwarded to the TypeSwimporting created
    """

    key_type, key_porting = swim.get_porting(key_type)
    value_type, value_porting = swim.get_porting(value_type)

    cpp_name = cpp_name.replace('?', key_type + ', ' + value_type)

    if key_porting.to_cpp_func and value_porting.to_cpp_func:
        to_cpp = FunctionBody.combine(key_porting.to_cpp_func, value_porting.to_cpp_func)(
            f"""
        void* kud = PACKED_UD(0);
        void* vud = PACKED_UD(1);
        {cpp_name} ret;

        auto keys = PyObject_CallMethod(input, "keys", nullptr);
        if (!keys){{
            PyErr_Clear();
            auto iter = PyObject_GetIter(input);
            if (!iter){{
                SWIM_RAISE_TYPE("expected an iterable, not ", input);
            }}
            PyObject* py_current;
            auto key_index = PyLong_FromLong(0);
            auto value_index = PyLong_FromLong(1);
            while (py_current = PyIter_Next(iter)){{
                auto key = PyObject_GetItem(py_current, key_index);
                if (!key) SWIM_RAISE_TYPE("expected 2-sequence in iterable, not ",py_current);
                auto value = PyObject_GetItem(py_current, value_index);
                if (!value) SWIM_RAISE_TYPE("expected 2-sequence in iterable, not ",py_current);
                auto cpp_k = {key_porting.to_cpp_func.function_name}(key, ok, kud);
                if (!ok || PyErr_Occurred()) SWIM_RAISE_UNSPECIFIED;
                ret[cpp_k] = {value_porting.to_cpp_func.function_name}(value, ok, vud);
                if (!ok || PyErr_Occurred()) SWIM_RAISE_UNSPECIFIED;
            }}
            Py_DECREF(iter);
            return ret;
        }}
        auto iter = PyObject_GetIter(keys);
        if (!iter){{
            SWIM_RAISE_TYPE("expected an iterable, not ", input);;
        }}
        PyObject* key;
        while (key = PyIter_Next(iter)){{
            auto value = PyObject_GetItem(input, key);
            if (!value) SWIM_RAISE_KEY("could not find key in mapping: ", key);
            auto cpp_k = {key_porting.to_cpp_func.function_name}(key, ok, kud);
            if (!ok || PyErr_Occurred()) SWIM_RAISE_UNSPECIFIED;
            ret[cpp_k] = {value_porting.to_cpp_func.function_name}(value, ok, vud);
            if (!ok || PyErr_Occurred()) SWIM_RAISE_UNSPECIFIED;
        }}
        Py_DECREF(iter);
        Py_DECREF(keys);
        return ret;
        """)

        to_cpp_check = """
        auto keys = PyObject_CallMethod(input, "keys", nullptr);
        PyObject* iter;
        if (keys){
            iter = PyObject_GetIter(keys);
        }
        else{
            iter = PyObject_GetIter(input);
        }
        bool ret = iter == nullptr;
        Py_XDECREF(keys);
        Py_XDECREF(iter);
        return ret;
        """
        if key_porting.to_cpp_post_func or value_porting.to_cpp_post_func:
            to_cpp_post = FunctionBody.combine(key_porting.to_cpp_post_func, value_porting.to_cpp_post_func)(
                f"""
            void* kud = PACKED_UD(0);
            void* vud = PACKED_UD(1);
            for (auto pair: input){{
            """
                + (
                    f'{key_porting.to_cpp_post_func.function_name}(pair.first, ok, kud); if (!ok || PyErr_Occurred()) return;'
                    if key_porting.to_cpp_post_func else '')
                + (
                    f'{value_porting.to_cpp_post_func.function_name}(pair.second, ok, vud); if (!ok || PyErr_Occurred()) return;'
                    if value_porting.to_cpp_post_func else '')
                + """
            }}
            """)
        else:
            to_cpp_post = None
    else:
        to_cpp = to_cpp_check = to_cpp_post = None

    if key_porting.to_py_func and value_porting.to_py_func:
        if output is dict:
            to_py = FunctionBody.combine(key_porting.to_py_func, value_porting.to_py_func)(f"""
                void* kud = PACKED_UD(0);
                void* vud = PACKED_UD(1);
                auto ret = PyDict_New();
                for (auto pair: input){{
                    auto key = {key_porting.to_py_func.function_name}(pair.first, ok, kud);
                    if (!ok || PyErr_Occurred()) {{ return ret; }}
                    auto value = {value_porting.to_py_func.function_name}(pair.second, ok, vud);
                    if (!ok || PyErr_Occurred()) {{ return ret; }}
                    if(PyDict_SetItem(ret ,key, value) != 0) {{ ok = false; return ret;}}
                }}
                return ret;
            """)
        elif output in (iter, list, tuple, set, frozenset):
            yield pools.tuple.get(key_type, value_type, swim=swim, pair=True)
            pair_type = 'std::pair<' + key_type + ', ' + value_type + '>'
            sub: TypeSwimporting = iter_.get(pair_type, cpp_name=cpp_name, input_=False, swim=swim, output=output)
            to_py = sub.to_py
        elif not output:
            to_py = None
        else:
            raise Exception('illegal output kind')
    else:
        to_py = None

    yield TypeSwimporting(cpp_name, 'Dict[' + key_porting.py_name + ', ' + value_porting.py_name + ']',
                          to_cpp=to_cpp,
                          to_py=to_py,
                          to_cpp_check=to_cpp_check,
                          to_cpp_post=to_cpp_post, **type_args)
