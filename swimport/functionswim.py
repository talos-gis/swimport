from typing import Union, List, Match, Optional, Iterable, Deque

import re
from collections import deque

from swimport.swim import Swim
from swimport.pools import Pool, syspools
from swimport.model import NameTrigger, Function, object_swimporting, Compileable, TriggerBehaviourSwimRule, SwimRule
from swimport.__util__ import *

MACRO_PATTERN = re.compile(r'\$({(?P<k_b>[^}]+)}|(?P<k>[a-zA-Z_0-9]+)|(?P<other>({}|.)))')
macro_dict = {'retvar': 'val', }


# todo python:cdefaultargs?

def apply_pycode_macros(code, env_dict=None, **kwargs):
    """apply special macros for python code"""
    d = env_dict
    if not d:
        d = kwargs
    elif kwargs:
        d = {**kwargs, **env_dict}

    def macro(match: Match[str]):
        match_string = match['k']
        if match_string:
            return macro_dict[match_string]
        match_string = match['k_b']
        if match_string:
            return str(eval(match_string, d))
        match_string = match['other']
        if match_string:
            if match_string == '$':
                return '$'
            raise ValueError('cannot match template code: $' + match_string)
        raise Exception('unrecognized match: ' + match.group())

    return MACRO_PATTERN.sub(macro, code)


@Function.Param.set_default_trigger
class ParameterNameTrigger(NameTrigger, Function.Param.Trigger):
    pass


class ParameterTypeTrigger(Function.Param.Trigger):
    """
    Trigger for specific parameters types.
    """

    def __init__(self, pattern: Compileable):
        self.pattern = re.compile(pattern)

    def is_valid(self, rule: 'SwimRule', obj: Function.Param):
        return super().is_valid(rule, obj) \
               and self.pattern.fullmatch(obj.normalized_type)

    const_ptr: 'ParameterTypeTrigger'
    not_const_ptr: 'ParameterTypeTrigger'


class ParameterBehaviour(Function.Param.Behaviour):
    """
    Trigger for a function parameter
    NOTE: unlike regular behaviours, this behaviour returns a ParameterUsageInfo.
    ParameterBehaviour object should not be used as a regular behaviour, since ParameterUsageInfo is not a Swimporting.
    """

    class ParameterUsageInfo:
        """An object representing how a parameter should be used"""

        def __init__(self):
            self.params_used: List[Function.Param] = []
            self.pre_decl_scopes: List = []
            self.post_decl_scopes: List = []
            self.pools = []

        def __bool__(self):
            return bool(self.params_used or self.pre_decl_scopes or self.post_decl_scopes or self.pools)

    def wrap(self, rule, param) -> ParameterUsageInfo:
        ret = self.ParameterUsageInfo()
        if param:
            ret.params_used.append(param)
        return ret


class ParameterRule(TriggerBehaviourSwimRule):
    def do(self, obj: Function.parameters) -> Optional[ParameterBehaviour.ParameterUsageInfo]:
        return super().do(obj)


ParameterBehaviour.rule_cls = ParameterRule


@Function.Param.set_default_behaviour
class ApplyBehaviour(ParameterBehaviour):
    """Applies keywords from another typemap to the parameter or parameters"""

    def __init__(self, *keywords: str, pools: Iterable[Pool] = ()):
        """
        :param keywords: rthe keywords to apply to the parameters, the number of keywords is the number of parameters consumed
        """
        self.keywords = keywords
        self.pools = pools

    def wrap(self, rule, param: Function.Param):
        ret = super().wrap(rule, None)
        ret.pools.extend(self.pools)
        if self.keywords:
            explanation = '// rule: ' + str(rule)
            copy_parts = []
            sign_parts = []
            for kw in self.keywords:
                if param is None:
                    # if we ran out of parameters unexpectedly, fail by returning an empty parameter usage info
                    return self.ParameterUsageInfo()
                ret.params_used.append(param)
                copy_parts.append(f'{param.type} {kw}')
                sign_parts.append(param.sign)
                param = param.next_or_none
            if len(copy_parts) == 1:
                copy_parts = copy_parts[0]
            else:
                copy_parts = '(' + ', '.join(copy_parts) + ')'

            if len(sign_parts) == 1:
                sign_parts = sign_parts[0]
            else:
                sign_parts = '(' + ', '.join(sign_parts) + ')'
            ret.pre_decl_scopes.append(
                Swim.add_raw(f'%apply {copy_parts} {{{sign_parts}}};' + explanation)
            )
            ret.post_decl_scopes.append(
                Swim.add_raw(f'%clear {sign_parts};' + explanation)
            )
        return ret


# region Triggers
# region NameTriggers
ParameterNameTrigger.ref_io = ParameterNameTrigger('IO_.*')
# endregion
# region TypeTriggers
ParameterTypeTrigger.ptr = ParameterTypeTrigger(r'.*[&*]')
ParameterTypeTrigger.const_ptr = ParameterTypeTrigger(r'.* const [&*]')
ParameterTypeTrigger.not_const_ptr = ParameterTypeTrigger.ptr & ~ParameterTypeTrigger.const_ptr
# endregion
# endregion
# region behaviours
ParameterBehaviour.default = ParameterBehaviour()
ParameterBehaviour.output = ApplyBehaviour('OUTPUT')
ParameterBehaviour.input = ApplyBehaviour('INPUT')
ParameterBehaviour.inout = ApplyBehaviour('INOUT')
# endregion
# region rules

ParameterRule.inout = ParameterRule(ParameterNameTrigger.ref_io,
                                    ParameterBehaviour.inout, 'inout')
ParameterRule.output = ParameterRule(ParameterTypeTrigger.not_const_ptr,
                                     ParameterBehaviour.output, 'out')
ParameterRule.input = ParameterRule(ParameterTypeTrigger.const_ptr,
                                    ParameterBehaviour.input, 'input')
ParameterRule.default = ParameterBehaviour.default


# endregion

@Function.set_default_behaviour
class FunctionBehaviour(Function.Behaviour):
    default_parameters_rules: Deque[ParameterRule] = deque((
        # regular
        ParameterRule.inout, ParameterRule.output,
        ParameterRule.input,
        # default
        ParameterRule.default
    ))

    def __init__(self, parameter_rules: List[ParameterRule] = ..., dll_detect=(),
                 prepend_python: str = None, append_python: str = None, exception_check=None, contract=None,
                 free_ret: Union[str, bool] = False, autodoc: Union[str, int, None] = 2,
                 docstring: str = None, body: str = '', body_scope: str = ...):
        """
        :param parameter_rules: rules for handling parameters
        :param dll_detect: dll detection dictionary
        :param prepend_python: python code to run before function is called
        :param append_python: python code to run after function is called
        :param exception_check: cpp code to check for and handle exceptions (see %exception in SWIG).
         use ... to check for all errors.
        :param contract: cpp contract for function (see %contract in SWIG)
        :param free_ret: whether to insert a clause to free the output of the function. set to True for delete,
        or specify a releasing function.
        :param autodoc: autodoc value for function (see %autodoc in SWIG)
        :param docstring: docstring for the function
        """
        if parameter_rules is ...:
            parameter_rules = self.default_parameters_rules
        self.parameter_rules: List[ParameterRule] = list(parameter_rules)
        self.dll_detect = dict(dll_detect)
        self.prepend = prepend_python
        self.append = append_python
        self.exception = exception_check
        self.contract = contract
        self.free_ret = free_ret
        self.autodoc = autodoc
        self.docstring = docstring
        self.body = body
        self.body_scope = body_scope

        if self.body:
            assert not self.dll_detect, 'function body must not be used with dll detect'

    @object_swimporting
    def wrap(self, rule, obj: Function, swim):
        post_decl_scopes = []
        pre_decl_scopes = []
        debug = {'parameter rules': [], 'dll name': []}

        swim.add_comment(f'{obj.name} ({rule})')

        body = self.body
        decl_slice = slice(0, None)

        # check for dll
        for dll_prefix, dll_name in self.dll_detect.items():
            if obj.return_type.startswith(dll_prefix):
                if dll_name.endswith('.dll'):
                    dll_name = dll_name[:-len('.dll')]
                clean_rtn_type = obj.return_type[len(dll_prefix):]
                decl_slice = slice(decl_slice.start + len(dll_prefix), decl_slice.stop, decl_slice.step)
                debug['dll name'].append(dll_name)
                swim.add_insert(
                    f'SWIM_DECL_IMPORTED_FUNC({clean_rtn_type},{obj.name}'
                    f', {", ".join(obj.prm_types)})')
                swim.add_init(f"SWIM_IMPORT_FROMDLL({obj.name}, {dll_name})")
                # note: if dll_detect exists, body must be initially empty
                body = '{\n\t' \
                       + ('' if clean_rtn_type.rstrip().endswith('void') else 'return ') \
                       + 'SWIM_FUNC_HANDLE_' + obj.name + '(' + ', '.join(obj.prm_names) + ');\n}'
                break

        # run through and assign rules to all the parameters
        next_param_ind = 0
        while len(obj.parameters) > next_param_ind:
            param = obj.parameters[next_param_ind]
            for param_rule in self.parameter_rules:
                usage = param_rule.do(param)
                if not usage:
                    continue

                for pool in usage.pools:
                    swim(pool)
                pre_decl_scopes.extend(usage.pre_decl_scopes)
                post_decl_scopes.extend(usage.post_decl_scopes)
                if not usage.params_used:
                    continue

                next_param_ind += len(usage.params_used)
                break
            else:
                raise Exception('parameter without rule: ' + param.body + ' at method ' + obj.name)

        # add all the special features:
        # region special features
        if self.append:
            append = apply_pycode_macros(self.append, method=obj)
            pre_decl_scopes.append(
                Swim.add_python_append(obj, append)
            )
            post_decl_scopes.append(
                Swim.add_python_append(obj, None)
            )

        if self.prepend:
            prepend = apply_pycode_macros(self.prepend, method=obj)
            pre_decl_scopes.append(
                Swim.add_python_prepend(obj, prepend)
            )
            post_decl_scopes.append(
                Swim.add_python_prepend(obj, None)
            )

        elif self.exception:
            if self.exception is ...:
                swim(syspools.std_exception)
                pre_decl_scopes.append(
                    Swim.add_raw('SWIM_STD_EXCEPTION(' + obj.pattern + ');')
                )
            else:
                exception = clean_source(self.exception)
                pre_decl_scopes.append(
                    Swim.add_exception_check(exception)
                )

            post_decl_scopes.append(Swim.add_raw('%exception;'))

        if self.contract:
            contract = clean_source(self.contract)
            pre_decl_scopes.append(
                Swim.add_contract(obj, contract)
            )
            post_decl_scopes.append(
                Swim.add_contract(obj, None)
            )

        if self.free_ret:
            free_out = self.free_ret
            if free_out is True:
                pre_decl_scopes.append(
                    Swim.add_raw('%newobject ' + obj.pattern + ';')
                )
            else:
                pre_decl_scopes.append(
                    Swim.add_raw('%typemap(ret) ' + obj.return_type + ' ' + obj.name + '{ ' + free_out + '($1); };')
                )
                post_decl_scopes.append(
                    Swim.add_raw('%typemap(ret) ' + obj.return_type + ' ' + obj.name + ';')
                )

        if self.autodoc is not None:
            pre_decl_scopes.append(
                Swim.add_raw(f'%feature("autodoc", "{self.autodoc}") ' + obj.pattern + ';')
            )
            post_decl_scopes.append(
                Swim.add_raw('%feature("autodoc") ' + obj.pattern + ';')
            )

        if self.docstring is not None:
            pre_decl_scopes.append(
                Swim.add_feature(self.docstring, obj.pattern, 'feature("docstring")')
            )
            post_decl_scopes.append(
                Swim.add_feature(self.docstring, None, 'feature("docstring")')
            )
        # endregion

        for scope in pre_decl_scopes:
            scope(swim)

        # actual deceleration goes here
        decl = obj.body[decl_slice]
        decl_scope = self.body_scope
        if body:
            if decl.endswith(';'):
                decl = decl[:-1]
            decl = decl + '\n' + body
        if decl_scope is ...:
            decl_scope = Swim.add_inline if body else Swim.add_raw
        decl_scope(swim, decl)

        for scope in reversed(post_decl_scopes):
            scope(swim)

        swim.add_comment(((n + ': ' + str(v)) for n, v in debug.items()),
                         verbosity_level=Verbosity.debug)

        swim.add_nl()


class FunctionNameTrigger(NameTrigger, Function.Trigger):
    pass


@Function.set_default_trigger
def default_trigger(arg=None):
    if arg is None:
        return Function.Trigger.inherit_cls()
    return FunctionNameTrigger(arg)
