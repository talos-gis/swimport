from typing import Union

import re

from swimport.__util__ import *
from swimport.swim import Swim
from swimport.pools import syspools
from swimport.functionswim import FunctionBehaviour
from swimport.model import Variable, NameTrigger, Compileable, object_swimporting, Container, Function, SwimRule


@Variable.set_default_trigger
class VariableNameTrigger(Variable.Trigger, NameTrigger):
    """trigger for a variable object"""


class VariableTypeTrigger(Variable.Trigger):
    """
    trigger for a variable object. See methodswim.ParameterTypeTrigger for an explanation on type matching
    """

    def __init__(self, pattern: Compileable):
        self.pattern = re.compile(pattern)

    def is_valid(self, rule: 'SwimRule', obj):
        return super().is_valid(rule, obj) \
               and self.pattern.fullmatch(obj.normalized_type)


def is_const(v: Variable):
    return re.search(r'(?<!a-zA-Z_0-9)const(?!a-zA-Z_0-9)', v.normalized_type)


@Variable.set_default_behaviour
class VariableBehaviour(Variable.Behaviour):
    """
    behaviour for variable object.
    """

    def __init__(self, immutable=False, const: bool = ..., del_from_module_ns=...):
        """
        :param immutable: whether to wrap the variable in an %immutable wrap
        :param const: whether to wrap the variable in a %constant directive. default is to check for const keyword in variable type.
        :param del_from_module_ns: whether to delete the variable from the module namespace, and make it only accessible from the cvar attribute. default is to only do this for immutable variables.
        """
        self.immutable = immutable
        self.const = const
        self.del_from_module_ns = del_from_module_ns

    @object_swimporting
    def wrap(self, rule, obj: Variable, swim):
        if self.immutable:
            swim.add_raw(f'%immutable {obj.name};')

        body = obj.body
        if body.startswith('extern '):
            body = body[len('extern '):]
        const = self.const
        if const is ...:
            # disable auto-const if obj is a variable subclass (like a class member)
            const = type(obj) is Variable \
                    and is_const(obj)

        if const:
            body = '%constant ' + body

        del_ = self.del_from_module_ns
        if del_ is ...:
            del_ = self.immutable

        if del_:
            swim(syspools.ns_trap(obj.name))

        swim.add_raw(body)


class VariableGetSetBehaviour(Variable.Behaviour):
    """
    A behaviour for variable objects that wraps the variable in getter and setter functions
    """
    default_get_behaviour = FunctionBehaviour()
    default_set_behaviour = FunctionBehaviour()

    def __init__(self, get: Union[str, bool] = True, set_: Union[str, bool] = ..., name_template='{}_{!l}',
                 get_behaviour=default_get_behaviour, set_behaviour=default_set_behaviour, decl_scope=...,
                 function_scope=..., func_class = ...):
        """
        :param get: whether to create a getter method. Can also be a string to give the getter a special name.
        :param set_: whether to create a setter method, default is to only create a setter if the variable is not a
         const. Can also be a string to give the setter a special name.
        :param name_template: a formattable string to generate the names of the getter and setter methods, note that
         the template uses extended formatting, see the ExtendedFormatter class in __util__.
        :param get_behaviour: the swimport method behaviour for getter methods.
        :param set_behaviour: the swimport method behaviour for setter methods.
        :param decl_scope: the scope of the variable declaration.
        :param function_scope: the scope of the function declaration.
        """
        self.get = get
        self.set = set_
        self.name_template = name_template
        self.get_behaviour = get_behaviour
        self.set_behaviour = set_behaviour
        self.decl_scope = decl_scope
        self.function_scope = function_scope
        self.func_class = func_class

    @object_swimporting
    def wrap(self, rule: 'SwimRule', obj: Variable, swim):
        swim.add_comment(obj)
        intype = obj.type
        qual_name = obj.name
        decl_scope = self.decl_scope
        function_scope = self.function_scope
        func_class = self.func_class
        setfunction_rtn_type = 'void'

        if isinstance(obj, Container.Member) and obj.is_static:
            if intype.startswith('static '):
                intype = intype[len('static '):]
            qual_name = obj.owner.name + '::' + qual_name
            setfunction_rtn_type = 'static void'

            if decl_scope is ...:
                decl_scope = None
            if function_scope is ...:
                function_scope = Swim.add_extend

        if decl_scope is ...:
            decl_scope = Swim.add_insert
        if function_scope is ...:
            function_scope = Swim.add_inline
        if func_class is ...:
            func_class = Function.make

        if decl_scope:
            decl_scope(swim, obj.body)

        if self.get:
            if isinstance(self.get, str):
                func_name = self.get
            else:
                func_name = ExtendedFormatter().format(self.name_template, 'get', obj.name)

            get_method = func_class(func_name, [], obj.type)
            behaviour = self.get_behaviour.replace(
                body=f'{{ return {qual_name}; }}',
                body_scope=function_scope)
            swim(behaviour.do(get_method))

        mk_set = self.set

        if mk_set is ...:
            mk_set = not is_const(obj)

        if mk_set:
            if isinstance(self.set, str):
                func_name = self.set
            else:
                func_name = ExtendedFormatter().format(self.name_template, 'set', obj.name)

            set_method = Function.make(func_name, [Function.Param.make('__v', intype)], setfunction_rtn_type)
            behaviour = self.set_behaviour.replace(
                body=f'{{ {qual_name} = __v; }}',
                body_scope=function_scope)
            swim(behaviour.do(set_method))
