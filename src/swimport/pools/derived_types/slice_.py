from swimport.pools.pools import pools, syspools
from swimport.pools.types import TypeSwimportingPool
from swimport.typeswim import TypeSwimporting, FunctionBody


@syspools.add(TypeSwimportingPool)
def slice_no_step(start_type, end_type, cpp_name, *, swim, **type_args):
    start_type, start_porting = swim.get_porting(start_type)
    end_type, end_porting = swim.get_porting(end_type)

    cpp_name = cpp_name.replace('?', f'{start_type}, {end_type}')

    if start_porting.to_py_func and end_porting.to_py_func:
        body = f"""
        ok = 1;
        PyObject* start = input.has_start ? 
            {start_porting.to_py_func.function_name}(input.start, ok, PACKED_UD(0)) :
             nullptr;
        if (!ok || PyErr_Occurred() != nullptr)
            return nullptr;
        PyObject* end = input.has_start ? 
            {end_porting.to_py_func.function_name}(input.end, ok, PACKED_UD(1)) :
             nullptr;
        if (!ok || PyErr_Occurred() != nullptr){{
            Py_DECREF(start);
            return nullptr;
        }}
        PyObject* ret = PySlice_New(start, end, nullptr);
        Py_XDECREF(start);
        Py_XDECREF(end);
        return ret;
        """
        to_py = FunctionBody.combine(start_porting.to_py_func, end_porting.to_py_func)(body)
    else:
        to_py = None

    if start_porting.to_cpp_func and end_porting.to_cpp_func:
        body = f"""
        ok = 1;
        if (!PySlice_Check(input))
            SWIM_RAISE_TYPE("expected a slice, not ", input);
        PyObject* step = PyObject_GetAttrString(input, "step");
        if (step != Py_None)
        {{
            Py_DECREF(step);
            SWIM_RAISE(PyExc_ValueError, "slice cannot have a specified step");
        }}
        Py_DECREF(step);
        {cpp_name} ret;

        PyObject* start = PyObject_GetAttrString(input, "start");
        if (start == Py_None)
            ret.has_start = false;
        else{{
            ret.start = {start_porting.to_cpp_func.function_name}(start, ok, PACKED_UD(0));
            if (!ok || PyErr_Occurred() != nullptr) {{
                Py_DECREF(start);
                return ret;
            }}
            ret.has_start = true;
        }}
        Py_DECREF(start);

        PyObject* end = PyObject_GetAttrString(input, "stop");
        if (end == Py_None)
            ret.has_end = false;
        else{{
            ret.end = {end_porting.to_cpp_func.function_name}(end, ok, PACKED_UD(1));
            if (!ok || PyErr_Occurred() != nullptr) {{
                Py_DECREF(end);
                return ret;
            }}
            ret.has_end = true;
        }}
        Py_DECREF(end);

        return ret;
        """
        to_cpp = FunctionBody.combine(start_porting.to_cpp_func, end_porting.to_cpp_func)(body)
    else:
        to_cpp = None

    if start_porting.to_cpp_check_func and end_porting.to_cpp_check_func:
        body = f"""
        if (!PySlice_Check(input))
            return 0;
        PyObject* step = PyObject_GetAttrString(input, "step");
        if (step != Py_None)
        {{
            Py_DECREF(step);
            return 0;
        }}
        Py_DECREF(step);

        PyObject* start = PyObject_GetAttrString(input, "start");
        if (start != Py_None)
        {{
            if (!{start_porting.to_cpp_check_func.function_name}(start, PACKED_UD(0))){{
                Py_DECREF(start);
                return 0;
            }}
        }}
        Py_DECREF(start);

        PyObject* end = PyObject_GetAttrString(input, "stop");
        if (end != Py_None){{
            if (!{end_porting.to_cpp_check_func.function_name}(end, PACKED_UD(1))){{
                Py_DECREF(end);
                return 0;
            }}
        }}
        Py_DECREF(end);

        return 1;
        """
        to_cpp_check = FunctionBody.combine(start_porting.to_cpp_check_func, end_porting.to_cpp_check_func)(body)
    else:
        to_cpp_check = None

    if start_porting.to_cpp_post_func or end_porting.to_cpp_post_func:
        body = f"""
        ok = 1;
        """
        if start_porting.to_cpp_post_func:
            body += f"""
            if (input.has_start){{
                {start_porting.to_cpp_post_func}(input.start, ok, PACKED_UD(0));
            }}
            """
        if end_porting.to_cpp_post_func:
            body += f"""
            if (input.has_end){{
                {end_porting.to_cpp_post_func}(input.end, ok, PACKED_UD(1));
            }}
            """
        to_cpp_post = FunctionBody.combine(start_porting.to_cpp_post_func, end_porting.to_cpp_post_func)(body)
    else:
        to_cpp_post = None

    return TypeSwimporting(cpp_name, 'slice',
                           to_py=to_py,
                           to_cpp=to_cpp,
                           to_cpp_check=to_cpp_check,
                           to_cpp_post=to_cpp_post,
                           **type_args)


@syspools.add(TypeSwimportingPool)
def slice_step(start_type, end_type, step_type, cpp_name, *, swim, **type_args):
    start_type, start_porting = swim.get_porting(start_type)
    end_type, end_porting = swim.get_porting(end_type)
    step_type, step_porting = swim.get_porting(step_type)

    cpp_name = cpp_name.replace('?', f'{start_type}, {end_type}, {step_type}')

    if start_porting.to_py_func and end_porting.to_py_func and step_porting.to_py_func:
        body = f"""
        ok = 1;
        PyObject* start = input.has_start ? 
            {start_porting.to_py_func.function_name}(input.start, ok, PACKED_UD(0)) :
             nullptr;
        if (!ok || PyErr_Occurred() != nullptr)
            return nullptr;
        PyObject* end = input.has_start ? 
            {end_porting.to_py_func.function_name}(input.end, ok, PACKED_UD(1)) :
             nullptr;
        if (!ok || PyErr_Occurred() != nullptr){{
            Py_DECREF(start);
            return nullptr;
        }}
        PyObject* step = input.has_step ? 
            {step_porting.to_py_func.function_name}(input.step, ok, PACKED_UD(2)) :
             nullptr;
        if (!ok || PyErr_Occurred() != nullptr){{
            Py_DECREF(start);
            Py_DECREF(end);
            return nullptr;
        }}
        PyObject* ret = PySlice_New(start, end, step);
        Py_XDECREF(start);
        Py_XDECREF(end);
        Py_XDECREF(step);
        return ret;
        """
        to_py = FunctionBody.combine(start_porting.to_py_func, end_porting.to_py_func, step_porting.to_py_func)(body)
    else:
        to_py = None

    if start_porting.to_cpp_func and end_porting.to_cpp_func and step_porting.to_cpp_func:
        body = f"""
        ok = 1;
        if (!PySlice_Check(input))
            SWIM_RAISE_TYPE("expected a slice, not ", input);
        {cpp_name} ret;

        PyObject* start = PyObject_GetAttrString(input, "start");
        if (start == Py_None)
            ret.has_start = false;
        else{{
            ret.start = {start_porting.to_cpp_func.function_name}(start, ok, PACKED_UD(0));
            if (!ok || PyErr_Occurred() != nullptr) {{            
                Py_DECREF(start);
                return ret;
            }}
            ret.has_start = true;
        }}
        Py_DECREF(start);

        PyObject* end = PyObject_GetAttrString(input, "stop");
        if (end == Py_None)
            ret.has_end = false;
        else{{
            ret.end = {end_porting.to_cpp_func.function_name}(end, ok, PACKED_UD(1));
            if (!ok || PyErr_Occurred() != nullptr) {{
                Py_DECREF(end);
                return ret;
            }}
            ret.has_end = true;
        }}
        Py_DECREF(end);

        PyObject* step = PyObject_GetAttrString(input, "step");
        if (step == Py_None)
            ret.has_step = false;
        else{{
            ret.step = {step_porting.to_cpp_func.function_name}(step, ok, PACKED_UD(2));
            if (!ok || PyErr_Occurred() != nullptr) {{
                Py_DECREF(step);
                return ret;
            }}
            ret.has_step = true;
        }}
        Py_DECREF(step);

        return ret;
        """
        to_cpp = FunctionBody.combine(start_porting.to_cpp_func, end_porting.to_cpp_func, step_porting.to_cpp_func)(
            body)
    else:
        to_cpp = None

    if start_porting.to_cpp_check_func and end_porting.to_cpp_check_func:
        body = f"""
        if (!PySlice_Check(input))
            return 0;

        PyObject* start = PyObject_GetAttrString(input, "start");
        if (start != Py_None)
        {{
            if (!{start_porting.to_cpp_check_func.function_name}(start, PACKED_UD(0))){{
                Py_DECREF(start);
                return 0;
            }}
        }}
        Py_DECREF(start);

        PyObject* end = PyObject_GetAttrString(input, "stop");
        if (end != Py_None){{
            if (!{end_porting.to_cpp_check_func.function_name}(end, PACKED_UD(1))){{
                Py_DECREF(end);
                return 0;
            }}
        }}
        Py_DECREF(end);

        PyObject* step = PyObject_GetAttrString(input, "step");
        if (step != Py_None){{
            if (!{step_porting.to_cpp_check_func.function_name}(step, PACKED_UD(2))){{
                Py_DECREF(step);
                return 0;
            }}
        }}
        Py_DECREF(step);

        return 1;
        """
        to_cpp_check = FunctionBody.combine(start_porting.to_cpp_check_func, end_porting.to_cpp_check_func,
                                            step_porting.to_cpp_check_func)(body)
    else:
        to_cpp_check = None

    if start_porting.to_cpp_post_func or end_porting.to_cpp_post_func:
        body = f"""
        ok = 1;
        """
        if start_porting.to_cpp_post_func:
            body += f"""
            if (input.has_start){{
                {start_porting.to_cpp_post_func}(input.start, ok, PACKED_UD(0));
            }}
            """
        if end_porting.to_cpp_post_func:
            body += f"""
            if (input.has_end){{
                {end_porting.to_cpp_post_func}(input.end, ok, PACKED_UD(1));
            }}
            """
        if step_porting.to_cpp_post_func:
            body += f"""
            if (input.has_step){{
                {step_porting.to_cpp_post_func}(input.step, ok, PACKED_UD(2));
            }}
            """
        to_cpp_post = FunctionBody.combine(start_porting.to_cpp_post_func, end_porting.to_cpp_post_func,
                                           step_porting.to_cpp_post_func)(body)
    else:
        to_cpp_post = None

    return TypeSwimporting(cpp_name, 'slice',
                           to_py=to_py,
                           to_cpp=to_cpp,
                           to_cpp_check=to_cpp_check,
                           to_cpp_post=to_cpp_post,
                           **type_args)


@pools.add(TypeSwimportingPool, name='slice')
def slice_(start_type, end_type=..., step_type=None, cpp_name='slice<?>', *, swim, **type_args):
    """
    typemaps for using slices for a set of types
    :param start_type: the name of the imported type for the start of the slice
    :param end_type: the name of the imported type for the start of the slice. default is to use start_type
    :param end_type: the name of the imported type for the start of the slice. default is to not allow steps.
        ... to use start_type
    :param cpp_name: the name of the cpp type to map for. ? will be replaced with the type names
    :param type_args: keyword parameters forwarded to the TypeSwimporting created
    """
    if end_type is ...:
        end_type = start_type
    if step_type is ...:
        step_type = start_type

    if step_type:
        return slice_step(start_type, end_type, step_type, cpp_name, swim, **type_args)
    else:
        return slice_no_step(start_type, end_type, cpp_name, swim, **type_args)