from typing import Type, Union
from enum import Enum

from swimport.typedefswim import TypedefBehaviour
from swimport.typeswim import TypeSwimporting
from swimport.pools import syspools, pools
from swimport.model import NameTrigger, Enumeration, object_swimporting, Typedef


@Enumeration.set_default_trigger
class EnumerationTrigger(NameTrigger, Enumeration.Trigger):
    pass


@Enumeration.set_default_behaviour
class EnumerationBehaviour(Enumeration.Behaviour):
    default_typedef_behaviour = TypedefBehaviour(no_declare=True)

    def __init__(self, typedef=..., typedef_behaviour=...):
        """
        :param typedef: typedef to apply to the enum, if any. default is to extract from the enum object.
        """
        self.typedef = typedef
        if typedef_behaviour is ...:
            typedef_behaviour = self.default_typedef_behaviour
        self.typedef_behaviour = typedef_behaviour

    @object_swimporting
    def wrap(self, rule, obj: Enumeration, swim):
        swim(pools.primitive())
        swim.add_comment(obj)
        swim.add_raw(obj.body)
        if self.typedef:
            if self.typedef is ...:
                self.typedef = obj.type
            typedef_swimporting = self.typedef_behaviour.do(Typedef.make(obj.name, self.typedef))
            swim.apply_porting(typedef_swimporting)


class EnumBehaviour(EnumerationBehaviour):
    """A behaviour to wrap an enumeration in a python enum class"""
    # each value is a tuple of the form:
    # (Py_BuildValue format character, PyLong_As*)
    _typedef_bindings = {
        'char': ('b', 'PyLong_AsLong'),
        'unsigned char': ('B', 'PyLong_AsUnsignedLong'),
        'short int': ('h', 'PyLong_AsLong'),
        'unsigned short int': ('H', 'PyLong_AsUnsignedLong'),
        'int': ('i', 'PyLong_AsLong'),
        'unsigned int': ('I', 'PyLong_AsUnsignedLong'),
        'long int': ('l', 'PyLong_AsLong'),
        'unsigned long int': ('k', 'PyLong_AsUnsignedLong'),
        'long long int': ('L', 'PyLong_AsLongLong'),
        'unsigned long long int': ('K', 'PyLong_AsUnsignedLongLong'),
    }
    _default_bindings = _typedef_bindings['int']

    def __init__(self, super_cls: Union[str, Type[Enum]] = 'enum.IntEnum', del_from_ns=True):
        """
        :param super_cls: the super class of the python enum.
        :param del_from_ns: whether to delete the globals constants in the module namespace.
        """
        super().__init__(typedef=None)  # no typedefs, we're gonna make our own typemaps for the python enum
        self.super_cls = super_cls
        self.del_from_ns = del_from_ns

    def module_and_type_names(self):
        if isinstance(self.super_cls, type):
            return self.super_cls.__module__, self.super_cls.__name__
        sep_index = self.super_cls.find('.')
        if sep_index < 0:
            # default module is enum
            return 'enum', self.super_cls
        return self.super_cls[:sep_index], self.super_cls[sep_index + 1:]

    @object_swimporting
    def wrap(self, rule: 'SwimRule', obj, swim):
        super().wrap(rule, obj, swim)

        # the enum must be on the cxx side so that the python class object will be present at compile time,
        # allowing the typemaps to bind
        enum_id = swim.create_unique_id('py_enum_' + obj.name)
        build_value_char, py_to_c_func = self._typedef_bindings.get(obj.type, self._default_bindings)
        mem_decl_list = ', '.join('"' + str(mem.name) + '", ' + str(mem.name) for mem in obj.members)
        call_format_string = '"s(' + (f"(s{build_value_char})" * len(obj.members)) + ')"'
        sup_mod, sup_cls = self.module_and_type_names()
        swim.add_insert(f"""
            PyObject* {enum_id}_cls;
        """)
        swim.add_init(f"""
            auto {enum_id}_enum_module = PyImport_ImportModule("{sup_mod}");

            if (!{enum_id}_enum_module)
                return nullptr;
            
            {enum_id}_cls = PyObject_CallMethod({enum_id}_enum_module
                , "{sup_cls}"
                , {call_format_string}
                , "{obj.name}"
                , {mem_decl_list});

            if (!{enum_id}_cls)
                return nullptr;
            
            Py_DECREF({enum_id}_enum_module);
            SWIG_Python_SetConstant(d, "{enum_id}_cls",{enum_id}_cls);
        """)
        swim.add_python(f"""
            {obj.name} = _example.{enum_id}_cls;
        """)

        type_swimporting = TypeSwimporting(obj.name, obj.name,
                                           to_py=f"""
                                            return PyObject_CallFunction({enum_id}_cls, "({build_value_char})", input);
                                            """,
                                           to_cpp=f"""
                                            if (!PyObject_IsInstance(input, {enum_id}_cls))
                                            {{
                                                ok = false;
                                                PyErr_SetString(PyExc_TypeError,"expected {obj.name}");
                                                return {{}};
                                            }}
                                            auto v = PyObject_GetAttrString(input, "value");
                                            if (!v)
                                            {{
                                                ok = false;
                                                return {{}}; 
                                            }}
                                            auto ret = static_cast<{obj.name}>({py_to_c_func}(v));
                                            Py_DECREF(v);
                                            return ret;
                                            """,
                                           to_cpp_check=f"""
                                            return PyObject_IsInstance(input, {enum_id}_cls);
                                            """)
        swim(type_swimporting)

        if self.del_from_ns:
            swim(syspools.ns_trap(*(m.name for m in obj.members)))
