from typing import Union, Iterable, Tuple, Iterator, Optional

from abc import ABC, abstractmethod
from functools import wraps

import swimport.pools as pools_pkg
from swimport.__util__ import *

"""
On the nature of the function bodies
I was presented with a challenge: we needed a simple way for functions to either return a value or indicate an error.
There are the following ways to do indicate an error:
I) raise an exception (SWIM_RAISE or another macro defined in pools.typemap_macros)
    this indicates that an error has occurred, the pros of doing this is that exceptions are easier to handle,
    they fall through subcallers, so it only needs to be caught in the typemap code itself. the cons are that throwing
    (not catching!) needs an insane amount of overhead. Note that in cpp_check and cpp_post functions, this usage is
    disabled for that reason.
II) set an indicator variable and return an arbitrary value (ok = false; / PyErr_SetString(...);)
    either through the ok variable or python's exception indicator, callers are obliged to check these variables after
    calling the function. The con of this method is that sometimes, building and returning an arbitrary value is
    impossible/more trouble than its worth.
"""


def typemap(x):
    if isinstance(x, str):
        return FunctionBody(x)
    return x


class ToPyTypemap(ABC):
    """
    Abstract class for typemap decelerations for converting from cpp to python
    """

    @abstractmethod
    def use_as_to_py(self, swim, swimporting: 'TypeSwimporting'):
        pass


class ToCppTypemap(ABC):
    """
    Abstract class for typemap decelerations for converting from python to cpp
    """

    @abstractmethod
    def use_as_to_cpp(self, swim, swimporting: 'TypeSwimporting'):
        pass


class ToCppPostTypemap(ABC):
    """
    Abstract class for typemaps for after converting from python to cpp
    """

    @abstractmethod
    def use_as_to_cpp_post(self, swim, swimporting: 'TypeSwimporting'):
        pass


class ToCppCheckTypemap(ABC):
    """
    Abstract class for typemap decelerations for checking a python object
    """

    @abstractmethod
    def use_as_to_cpp_check(self, swim, swimporting: 'TypeSwimporting'):
        pass


class FunctionBody(ToPyTypemap, ToCppTypemap, ToCppCheckTypemap, ToCppPostTypemap, Replaceable):
    """
    A typemap to create a function wrapper around a body
    """
    @property
    def can_replace(self):
        return not self.owner

    def __init__(self, body, *, user_data='', fragments=()):
        """
        :param body: the function body. The function returns void and has 4 parameters:
            * T input, either of type PyObject* or the type being mapped
            * int& ok, set it to false to indicate an error
            * void * userdata, generic data supplied by the typemap creator
            * T* ret, either of type PyObject* or the type being mapped, stores the result.
        :param user_data: code to assign to an existing variable called userdata, before the function is called.
        :param fragments: a tuple of fragment names to assign to the typemap (in addition to the function fragment)
        """
        self.body = body
        self.user_data = user_data
        self.fragments = fragments

        self.function_name = None
        self.owner: TypeSwimporting = None

    def set_owner(self, owner):
        if self.owner is not None:
            raise Exception('function typemap is already owned by ' + self.owner.cpp_name)
        self.owner = owner

    def use_as_to_py(self, swim, swimporting):
        swimporting.to_py_func = self
        self.set_owner(swimporting)

        self.function_name = to_py_func = swim.add_function('PyObject*', ('ToPy', swimporting.cpp_name), self.body,
                                                            (swimporting.cpp_name + ' const & input', 'int& ok',
                                                             'void * volatile userdata'),
                                                            fragments=self.fragments)
        swim.add_raw(f"""
                    %typemap(out, fragment="{to_py_func}") {swimporting.cpp_name}{{
                        void * volatile userdata = nullptr;
                        int ok = true;
                        {self.user_data}
                        try{{
                            $result = {to_py_func}($1, ok, userdata);
                        }}
                        catch(std::exception const& e){{ PyErr_SetString(PyExc_Exception, e.what()); SWIG_fail;}}
                        catch(std::pair<PyObject*, std::string> const & p) {{
                            std::string msg = "error in converting output in function $symname: ";
                            msg += std::get<1>(p);
                            PyErr_SetString(std::get<0>(p), msg.c_str()); SWIG_fail;
                        }}
                        if (!ok || PyErr_Occurred() != nullptr) SWIG_fail;
                    }}
                    """)

        if swimporting.out_maps:
            swim.add_raw(f"""
                        %typemap(in, numinputs=0) {swimporting.cpp_name} *OUTPUT ({swimporting.cpp_name} res = 
                            {swimporting.arbitrary_initializer}){{
                            $1=($1_ltype)(&res);
                        }}
                        %typemap(argout, fragment="{to_py_func}") {swimporting.cpp_name} *OUTPUT{{
                            if ($1){{
                                void * volatile userdata = nullptr;
                                int ok = true;
                                {self.user_data}
                                PyObject* to_add = nullptr;
                                try {{
                                    to_add = {to_py_func}(*$1, ok, userdata);
                                }}
                                catch(std::exception const& e){{ PyErr_SetString(PyExc_Exception, e.what()); SWIG_fail;}}
                                catch(std::pair<PyObject*, std::string> const & p) {{
                                    std::string msg = "error in converting out parameter (#$argnum) in function $symname: ";
                                    msg += std::get<1>(p);
                                    PyErr_SetString(std::get<0>(p), msg.c_str()); SWIG_fail;
                                }}
                                if (!ok || PyErr_Occurred() != nullptr) SWIG_fail;
                                $result = SWIG_Python_AppendOutput($result, to_add);
                            }}
                        }}
                        """)

        if swimporting.varin_maps:
            swim.add_raw(f"""
                        %typemap(varout, fragment="{to_py_func}") {swimporting.cpp_name}{{
                            int ok = 1;
                            void * volatile userdata = nullptr;
                            {self.user_data}
                            try {{
                                $result = {to_py_func}($1, ok, userdata);
                            }}
                            catch(std::exception const& e){{ PyErr_SetString(PyExc_Exception, e.what()); return nullptr;}}
                            catch(std::pair<PyObject*, std::string> const & p) {{
                                std::string msg = "error in converting variable $symname to py: ";
                                msg += std::get<1>(p);
                                PyErr_SetString(std::get<0>(p), msg.c_str()); return nullptr;
                            }}
                            if (!ok || PyErr_Occurred() != nullptr) return nullptr;
                        }}
                        %typemap(constcode, fragment="{to_py_func}") {swimporting.cpp_name}{{
                            int ok = 1;
                            void * volatile userdata = nullptr;
                            {self.user_data}
                            PyObject* result = nullptr;
                            try {{
                            result = {to_py_func}($1, ok, userdata);
                            }}
                            catch(std::exception const& e){{ PyErr_SetString(PyExc_Exception, e.what()); return nullptr;}}
                            catch(std::pair<PyObject*, std::string> const & p) {{
                                std::string msg = "error in converting variable $symname to py: ";
                                msg += std::get<1>(p);
                                PyErr_SetString(std::get<0>(p), msg.c_str()); return nullptr;
                            }}
                            if (!ok || PyErr_Occurred() != nullptr) return nullptr;
    
                            SWIG_Python_SetConstant(d, "$symname",result);
                        }}
                        """)

        if swimporting.directorout_maps:
            swim.add_raw(f"""
            %typemap(directorin, fragment="{to_py_func}") {swimporting.cpp_name} {{
                void * volatile userdata = nullptr;
                int ok = true;
                {self.user_data}
                $input = {to_py_func}($1, ok, userdata);
                if (!ok || PyErr_Occurred() != nullptr) SWIM_THROW_UNSPECIFIED_VAR($1);
            }}
            """)

    def use_as_to_cpp(self, swim, swimporting):
        self.set_owner(swimporting)

        self.function_name = to_cpp_func = swim.add_function(swimporting.cpp_name, ('ToCpp', swimporting.cpp_name),
                                                             self.body,
                                                             ('PyObject * input', 'int& ok', 'void * volatile userdata'),
                                                             fragments=self.fragments)
        swimporting.to_cpp_func = self
        swim.add_raw(f"""
                    %typemap(in, fragment="{to_cpp_func}") {swimporting.cpp_name}{{
                        void * volatile userdata = nullptr;
                        {self.user_data}
                        int ok = true;
                        try{{
                            $1 = ($1_ltype){to_cpp_func}($input, ok, userdata);;
                        }}
                        catch(std::exception const& e){{ PyErr_SetString(PyExc_Exception, e.what()); SWIG_fail;}}
                        catch(std::pair<PyObject*, std::string> const & p) {{
                            std::string msg = "error in converting parameter #$argnum in function $symname: ";
                            msg += std::get<1>(p);
                            PyErr_SetString(std::get<0>(p), msg.c_str()); SWIG_fail;
                        }}
                        if (!ok || PyErr_Occurred() != nullptr) SWIG_fail;
                    }}
                    """)

        if swimporting.ref_maps:
            swim(pools_pkg.pools.include("<typeinfo>"))
            swim.add_raw(f"""
                        %typemap(in, fragment="{to_cpp_func}") {swimporting.cpp_name} const * INPUT ({swimporting.cpp_name} res = {swimporting.arbitrary_initializer}){{
                        """ +
                         (f"""
                            if ((typeid($1_type) == typeid({swimporting.cpp_name} const*))
                                && ($input == Py_None)){{
                                $1 = nullptr;
                            }}
                            else
                            """ if swimporting.ref_maps is not swimporting.REF_MAPS_NO_NONE_CHECK else "")
                         +
                         f"""
                            {{
                                void * volatile userdata = nullptr;
                                int ok = true;
                                {self.user_data}
                                try {{
                                    res = {to_cpp_func}($input, ok, userdata);
                                    $1 = ($1_ltype)&res;
                                }}
                                catch(std::exception const& e){{ PyErr_SetString(PyExc_Exception, e.what()); SWIG_fail;}}
                                catch(std::pair<PyObject*, std::string> const & p) {{
                                    std::string msg = "error in converting parameter #$argnum in function $symname: ";
                                    msg += std::get<1>(p);
                                    PyErr_SetString(std::get<0>(p), msg.c_str()); SWIG_fail;
                                }}
                                if (!ok || PyErr_Occurred() != nullptr) SWIG_fail;
                            }}
                        }}
                        """)

        if swimporting.varin_maps:
            swim.add_raw(f"""
                        %typemap(varin, fragment="{to_cpp_func}") {swimporting.cpp_name}{{
                            int ok = 1;
                            void * volatile userdata = nullptr;
                            {self.user_data}
                            try {{
                                {swimporting.cpp_name} temp = {to_cpp_func}($input, ok, userdata);
                                $1 = temp;
                            }}
                            catch(std::exception const& e){{ PyErr_SetString(PyExc_Exception, e.what()); SWIG_fail;}}
                            catch(std::pair<PyObject*, std::string> const & p) {{
                                std::string msg = "error in setting variable $symname from py: ";
                                msg += std::get<1>(p);
                                PyErr_SetString(std::get<0>(p), msg.c_str()); SWIG_fail;
                            }}
                            if (!ok || PyErr_Occurred() != nullptr) SWIG_fail;
                        }}
                        """)

        if swimporting.directorout_maps:
            swim.add_raw(f"""
                        %typemap(directorout, fragment="{to_cpp_func}") {swimporting.cpp_name}{{
                            int ok = 1;
                            void * volatile userdata = nullptr;
                            {self.user_data}
                            $result = {to_cpp_func}($input, ok, userdata);
                            if (!ok || PyErr_Occurred() != nullptr) SWIM_RAISE_UNSPECIFIED_VAR($input);
                        }}
                        """)

    def use_as_to_cpp_check(self, swim, swimporting):
        self.set_owner(swimporting)

        self.function_name = to_cpp_check_func = swim.add_function('bool', ('ToCppCheck', swimporting.cpp_name),
                                                                   self.body,
                                                                   ('PyObject * input',
                                                                    'void * volatile userdata'), fragments=self.fragments)
        swimporting.to_cpp_check_func = self
        swim.add_raw(f"""
                    %typemap(typecheck{swimporting.to_cpp_check_precedence_arg}, fragment="{to_cpp_check_func}") {swimporting.cpp_name}{{
                        void * volatile userdata=nullptr;
                        {self.user_data}
                        $1 = {to_cpp_check_func}($input, userdata);
                        if (PyErr_Occurred() != nullptr){{
                            $1 = 0;
                            PyErr_Clear();
                        }}
                     }}
                     """)
        if swimporting.ref_maps:
            swim.add_raw(f"""
                        %typemap(typecheck{swimporting.to_cpp_check_precedence_arg}, fragment="{to_cpp_check_func}") {swimporting.cpp_name} const * INPUT{{
                            void * volatile userdata=nullptr;
                            {self.user_data}
                            $1={to_cpp_check_func}($input, userdata);
                            if (PyErr_Occurred() != nullptr){{
                                $1 = 0;
                                PyErr_Clear();
                            }}
                         }}
                         """)

    def use_as_to_cpp_post(self, swim, swimporting: 'TypeSwimporting'):
        self.set_owner(swimporting)

        self.function_name = to_cpp_post_func = swim.add_function('void', ('ToCppPost', swimporting.cpp_name),
                                                                  self.body,
                                                                  (swimporting.cpp_name + ' input', 'int& ok',
                                                                   'void * volatile userdata'),
                                                                  fragments=self.fragments)
        swimporting.to_cpp_post_func = self
        swim.add_raw(f"""
                    %typemap(argout, fragment="{to_cpp_post_func}") {swimporting.cpp_name}{{
                        void * volatile userdata = nullptr;
                        int ok = true;
                        {self.user_data}
                        {to_cpp_post_func}($1, ok, userdata);
                        if (!ok || PyErr_Occurred() != nullptr) SWIG_fail;
                    }}
                    """)

        if swimporting.ref_maps:
            swim.add_raw(f"""
                        %typemap(argout, fragment="{to_cpp_post_func}") {swimporting.cpp_name} const * INPUT{{
                            if ($1)
                            {{
                                void * volatile userdata = nullptr;
                                int ok = true;
                                {self.user_data}
                                {to_cpp_post_func}(*$1, ok, userdata);
                                if (!ok || PyErr_Occurred() != nullptr) SWIG_fail;
                            }}
                        }}
                        """)

    @classmethod
    def combine(cls, *functions: 'FunctionBody'):
        userdata = [f'void * volatile ud[{len(functions)}] = {{}};'
                    f'  // the ud must be volatile because otherwise the compiler inlines it as an expression.']
        frags = []
        for i, fb in enumerate(functions):
            if not fb:
                continue
            if fb.user_data:
                userdata.append(f"""
{{
    void * volatile userdata=nullptr;  // userdata for type {fb.owner.cpp_name}
    {{
    {fb.user_data}
    }}
    ud[{i}] = userdata;  // userdata for type {fb.owner.cpp_name}
}}
""")
            frags.append(fb.function_name)
            frags.extend(fb.fragments)
        userdata.append('userdata = (void * volatile)ud;')
        userdata = '\n'.join(userdata)

        @wraps(FunctionBody.__init__)
        def init(*args, fragments=(), **kwargs):
            if fragments:
                f = list(fragments) + frags
            else:
                f = frags
            return cls(*args, fragments=f, user_data=userdata, **kwargs)

        return init

    @property
    def frags(self):
        return tuple((*self.fragments, self.function_name))


class DefaultCppCheck(ToCppCheckTypemap):
    """
    A class to create a to_cpp_check typemap using the already provided tocpp typemap.
    """

    def use_as_to_cpp_check(self, swim, swimporting):
        std_to_cpp = swimporting.to_cpp_func.function_name
        if not std_to_cpp:
            raise Exception(
                'DefaultCppCheck was declared, but a standard to cpp function was not declared for this type')

        FunctionBody(f"""
            int result = 1;
            try{{
                {std_to_cpp}(input, result, userdata);
            }}
            catch(...) {{result = 0;}}
            if (PyErr_Occurred() != nullptr)
            {{
                result = 0;
                PyErr_Clear();
            }}
            return result;
        """).use_as_to_cpp_check(swim, swimporting)


class BuiltinTypemap(ToPyTypemap, ToCppTypemap, ToCppCheckTypemap):
    """A typemap that applies the builtin ptr typemaps"""

    def __init__(self, type_, **additional_args):
        self.type_ = type_
        self.additional_args = additional_args

    def use_as_to_py(self, swim, swimporting: 'TypeSwimporting'):
        new_name = swimporting.cpp_name
        if new_name.endswith('*'):
            new_name = new_name[:-1]
        FunctionBody(f"""
        return SWIG_NewPointerObj(new {new_name}(*input), 
            (swig_type_info*)userdata, SWIG_POINTER_OWN |  0 );
        """, user_data=f'userdata = $descriptor({self.type_});', **self.additional_args) \
            .use_as_to_py(swim, swimporting)

    def use_as_to_cpp(self, swim, swimporting: 'TypeSwimporting'):
        FunctionBody(f"""
        void* argp;
        auto res = SWIG_ConvertPtr(input, &argp, (swig_type_info*)userdata,  0  | 0);
        if (!SWIG_IsOK(res)) {{
            PyErr_SetString(PyExc_TypeError, "bad type");
            ok = false;
            return nullptr;
        }}
        if (!argp) {{
            PyErr_SetString(PyExc_ValueError, "null pointer");
            ok = false;
            return nullptr;
        }} else {{
           auto temp = reinterpret_cast<{swimporting.cpp_name}>(argp);
           return temp;
        }}
        ok = false;
        return nullptr;
        """, user_data=f'userdata = $descriptor({self.type_});', **self.additional_args) \
            .use_as_to_cpp(swim, swimporting)

    def use_as_to_cpp_check(self, swim, swimporting: 'TypeSwimporting'):
        FunctionBody(f"""
        void* argp;
        auto res = SWIG_ConvertPtr(input, &argp, (swig_type_info*)userdata,  0  | 0);
        if (!SWIG_IsOK(res)) {{
            return false;
        }}
        if (!argp) {{
            return false;
        }} else {{
           return true;
        }}
        """, user_data=f'userdata = $descriptor({self.type_});', **self.additional_args) \
            .use_as_to_cpp_check(swim, swimporting)


class TypeSwimporting(Replaceable):
    """A swimporting for a custom type"""
    default_in_iter_types = ['py_iterable<?>']
    default_out_iter_types = ['std::vector<?>']

    ENSURE_UNIQUE_SKIP_IF_EXISTS = object()
    REF_MAPS_NO_NONE_CHECK = object()

    @classmethod
    def normalize_maps_list(cls, oim, default) -> Iterator[Tuple[str, int, dict]]:
        for im in oim:
            if im is ...:
                yield from default
            else:
                yield im

    def __init__(self, cpp_name: str, py_name: str = None, *,
                 to_py: Union[ToPyTypemap, str, None] = None,
                 to_cpp: Union[ToCppTypemap, str, None] = None,
                 to_cpp_check: Union[ToCppCheckTypemap, str, None] = DefaultCppCheck(),
                 to_cpp_post: Union[ToCppPostTypemap, str, None] = None,

                 out_maps=True, ref_maps=True, inout_maps=...,
                 varin_maps=True, varout_maps=True,
                 directorout_maps=..., directorin_maps=True,

                 in_iterable_types: Iterable[Union[str, type(...)]] = (...,),
                 out_iterable_types: Iterable[Union[str, type(...)]] = (...,),
                 to_cpp_check_precedence: Union[str, int] = None,
                 arbitrary_initializer='{}',
                 ensure_unique=True,
                 aliases=()):

        """
        :param cpp_name: the cpp name of the type
        :param py_name: the python name of the type (only used in comments)
        :param to_py: typemap for py->cpp conversion
        :param to_cpp: typemap for cpp->py conversion
        :param to_cpp_check: typemap for checking python objects. default is to call to_cpp and check for Py_Err.
            only applicable if to_cpp is entered.
        :param out_maps: whether to apply output typemaps to the object. only applicable if to_py is entered.
        :param ref_maps: whether to apply typemaps to reference objects. only applicable if to_cpp is entered.
        :param inout_maps: whether to apply typemaps for inout reference parameters.
            Default is to only apply if all other maps are defined.
        :param varin_maps: whether to apply input maps for global variables of the type.
            only applicable if to_cpp is entered.
        :param varout_maps: whether to apply output maps for global variables of the type.
            only applicable if to_py is entered.
        :param directorout_maps: whether to apply input maps for director functions of the type.
            only applicable if to_cpp is entered. Default is not to apply if to_cpp_post is used.
        :param directorin_maps: whether to apply output maps for director functions of the type.
            only applicable if to_py is entered.
        :param in_iterable_types: the depth of the input iterable mapping.
        :param out_iterable_types: the depth of the output iterable mapping.
            can also specify different depths for different types.
            A ... represents the default types.
        :param to_cpp_check_precedence: the precedence of the typecheck typemap.
            ... for maximum integer value.
        :param arbitrary_initializer: a valid initialization list for the cpp type. Creating a valid arbitrary value
            that can be overridden/deleted.
        :param ensure_unique: raise an exception if a type of the same same name was already imported. Disabling
            this might silence errors down the road.
            Setting to ... will instead skip the porting if the type already exists.
        :param aliases: additional names to copy all typemaps to.
        """
        super().__init__()
        self.cpp_name = cpp_name
        self._py_name = py_name
        self.to_py = typemap(to_py)
        self.to_cpp = typemap(to_cpp)
        self.to_cpp_check = typemap(to_cpp_check)
        self.to_cpp_post = typemap(to_cpp_post)
        self.out_maps = out_maps
        self.ref_maps = ref_maps
        self.inout_maps = inout_maps

        self.varin_maps = varin_maps
        self.varout_maps = varout_maps

        self.directorin_maps = directorin_maps
        self.directorout_maps = directorout_maps

        self.to_cpp_check_precedence = to_cpp_check_precedence
        self.arbitrary_initializer = arbitrary_initializer

        self.out_iterable_types = out_iterable_types
        self.in_iterable_types = in_iterable_types

        self.to_py_func: Optional[FunctionBody] = None
        self.to_cpp_func: Optional[FunctionBody] = None
        self.to_cpp_check_func: Optional[FunctionBody] = None
        self.to_cpp_post_func: Optional[FunctionBody] = None
        self.assigned = False

        self.ensure_unique = ensure_unique
        self.aliases = aliases

        if self.inout_maps:
            if not all((self.to_py, self.to_cpp, self.ref_maps, self.out_maps)):
                if self.inout_maps is ...:
                    self.inout_maps = False
                else:
                    raise ValueError('inout_typemaps can only be applied if all other primary maps are enabled')
        if self.directorout_maps is ...:
            self.directorout_map = not self.to_cpp_post

    @property
    def can_replace(self):
        return not self.assigned

    @property
    def py_name(self):
        return self._py_name or 'Any'

    @property
    def to_cpp_check_precedence_arg(self):
        precedence = self.to_cpp_check_precedence
        if precedence is ...:
            precedence = '32767'

        if precedence is not None:
            return ', precedence=' + str(precedence)
        return ''

    def _set_type(self, swim, name):
        if self.ensure_unique:
            prev = swim.types.get(name)
            if prev:
                if self.ensure_unique is self.ENSURE_UNIQUE_SKIP_IF_EXISTS:
                    return False
                raise Exception(f'type {name} was already imported by swimporting: {prev}')

        swim.types[name] = self
        return True

    def __call__(self, swim):
        swim(pools_pkg.syspools.typemap_macros)

        if not self._set_type(swim, self.cpp_name):
            return False

        if self.py_name:
            swim.add_comment(f'type: {self.cpp_name}->{self.py_name}')
        else:
            swim.add_comment(f'type: {self.cpp_name}')

        if self.to_py:
            self.to_py.use_as_to_py(swim, self)

        if self.to_cpp:
            self.to_cpp.use_as_to_cpp(swim, self)
            if self.to_cpp_check:
                self.to_cpp_check.use_as_to_cpp_check(swim, self)
            if self.to_cpp_post:
                self.to_cpp_post.use_as_to_cpp_post(swim, self)

        if self.to_py:
            for mname in self.normalize_maps_list(self.out_iterable_types,
                                                  self.default_out_iter_types):
                swim(pools_pkg.pools.iter(self.cpp_name, cpp_name=mname))

            if self.out_maps:
                swim.add_raw(f"""%apply {self.cpp_name} * OUTPUT {{{self.cpp_name} & OUTPUT}};""")

        if self.to_cpp:
            for mname in self.normalize_maps_list(self.in_iterable_types, self.default_in_iter_types):
                swim(pools_pkg.pools.input_iterable(self.cpp_name, cpp_name=mname))

            if self.ref_maps:
                swim.add_raw(f"""%apply {self.cpp_name} const * INPUT {{{self.cpp_name} const & INPUT}};""")

        if self.inout_maps:
            swim.add_raw(f"""
                        %typemap(argout) {self.cpp_name} * INOUT = {self.cpp_name} *OUTPUT;
                        %typemap(in) {self.cpp_name} *INOUT = {self.cpp_name} const * INPUT;
                        %typemap(typecheck{self.to_cpp_check_precedence_arg}) {self.cpp_name} *INOUT = {self.cpp_name} const * INPUT;
                        %apply {self.cpp_name} * INOUT {{{self.cpp_name} & INOUT}};
                        """)

        for alias in self.aliases:
            if not self._set_type(swim, alias):
                continue
            swim.add_raw("%apply " + self.cpp_name + ' {' + alias + '};')

        swim.add_nl()
        self.assigned = True

        return True
