from typing import List, Optional, Union, TextIO, MutableMapping, Any, Tuple, Type

from functools import lru_cache
from os import PathLike, fspath
import itertools as it

import swimport.pools as pools_pkg
from swimport.model import SwimportAggregate, CPPObject, Swimporting, Function
from swimport.typeswim import TypeSwimporting
from swimport.__util__ import *


class Delaying:
    """A wrapper descriptor for functions so they can be called as parting functions from the owner class"""

    def __init__(self, func):
        self.__func__ = func

    @lru_cache(None)
    def parting(self, owner_cls):
        def ret(*args, **kwargs):
            if args and isinstance(args[0], owner_cls):
                return self.__func__(*args, **kwargs)
            return lambda s: self.__func__(s, *args, **kwargs)

        return ret

    def __get__(self, instance, owner):
        if instance is None:
            return self.parting(owner)
        return self.__func__.__get__(instance)

    def __call__(self, *args, **kwargs):
        return self.__func__(*args, **kwargs)


class Swim(SwimportAggregate):
    """The main swim object, absorbs all the lines and scopes given by swimportings"""

    def __init__(self, module_name: Optional[str], disclose=True, verbosity: Verbosity = Verbosity.info, **kwargs):
        """
        :param module_name: the name of the module, if this is set, the module pool will be automatically added
        :param disclose: whether to automatically add the disclose pool
        :param verbosity: the verbosity of the swim
        :param kwargs: additional arguments fed to the module pool
        """
        # note: special swimportings can place their markers here even though they are NOT cppObjects
        self.imported: MutableMapping[CPPObject, Any] = {}
        self.types: MutableMapping[str, TypeSwimporting] = {}
        self.lines: List[str] = []
        self.module_name = module_name
        self.id_mark = 'SWIM_MAIN' if not module_name else ('SWIM_' + module_name.upper())
        self.verbosity = verbosity

        if disclose:
            self(pools_pkg.pools.disclose)
        if module_name:
            self(pools_pkg.pools.module(module_name, **kwargs))

    def apply_porting(self, swimporting: Swimporting) -> Union[str, int]:
        """
        Apply a single porting to the swim
        :returns: whether or not the porting succeeded
        """
        if swimporting(self):
            obj = getattr(swimporting, 'object', None)
            if obj:
                return obj.name
            return 1
        return 0

    def _add_scope(self, *args, **kwargs):
        """
        adds lines to the swim object. with the arguments forwarded to __util__.scope_lines
        :returns int: the number of lines added
        """
        lines = scope_lines(*args, **kwargs)
        self.lines.extend(lines)
        return len(lines)

    @Delaying
    def add_raw(self, lines):
        """
        add lines to the swim without an enclosing scope
        """
        return self._add_scope(lines, None, None, indent=None, inline=False)

    @Delaying
    def add_extend(self, lines, name=''):
        """
        add lines to the swim without an enclosing scope
        """
        return self._add_scope(lines, '%extend ' + name + '{', '}', indent=None, inline=False)

    @Delaying
    def add_insert(self, lines):
        """
        add lines to the swim with an insert scope %{ %}
        """
        return self._add_scope(lines, '%{', '%}')

    @Delaying
    def add_init(self, lines):
        """
        add lines to the swim with an %init scope
        """
        return self._add_scope(lines, '%init %{', '%}')

    @Delaying
    def add_begin(self, lines):
        """
        add lines to the swim with an %init scope
        """
        return self._add_scope(lines, '%begin %{', '%}')

    @Delaying
    def add_inline(self, lines):
        """
        add lines to the swim with an %inline scope
        """
        return self._add_scope(lines, '%inline %{', '%}')

    @Delaying
    def add_python(self, lines):
        """
        add lines to the swim with a %pythoncode scope
        """
        return self._add_scope(lines, '%pythoncode %{', '%}', inline=False)

    @Delaying
    def add_python_begin(self, lines):
        """
        add lines to the swim with a %pythonbegin scope
        """
        return self._add_scope(lines, '%pythonbegin %{', '%}', inline=False)

    @Delaying
    def add_feature(self, lines, pattern, keyword):
        if lines:
            return self._add_scope(lines, '%' + keyword + ' ' + pattern + ' %{', '%}', inline=False)
        else:
            return self.add_raw('%' + keyword + ' ' + pattern + ';')

    @Delaying
    def add_python_append(self, method: Function, lines):
        """
        add lines to the swim with a %pythonappend scope. requires the method to which to bind.
        """
        return self.add_feature(lines, method.pattern, 'pythonappend')

    @Delaying
    def add_python_prepend(self, method: Function, lines):
        """
        add lines to the swim with a %pythonprepend scope. requires the method to which to bind.
        """
        return self.add_feature(lines, method.pattern, 'pythonprepend')

    @Delaying
    def add_exception_check(self, lines):
        """
        add lines to the swim with a %exception scope. requires the method to which to bind.
        """
        return self.add_feature(lines, '', 'exception')

    @Delaying
    def add_contract(self, method: Function, lines):
        """
        add lines to the swim with a %contract scope. requires the method to which to bind.
        """
        return self.add_feature(lines, method.pattern, 'contract')

    @Delaying
    def add_comment(self, lines, verbosity_level=Verbosity.info):
        """
        adds lines as a collection of singleline comments
        """
        if self.verbosity < verbosity_level:
            return 0
        return self._add_scope(lines, None, None, '// ', inline=False)

    @Delaying
    def add_comment_ml(self, lines, verbosity_level=Verbosity.info):
        """
        adds lines as a multiline comment
        """
        if self.verbosity < verbosity_level:
            return 0
        return self._add_scope(lines, '/*', '*/', '* ', inline=False)

    def create_unique_id(self, id_seed: str):
        ret = f'__SWIMPORT_{self.id_mark}_{clean_identifier(id_seed)}'
        return ret

    def add_function(self, return_type: str, function_name: str, lines, arguments: list, add_scope=add_raw, *,
                     name_abs=False, fragments=()) -> str:
        """
        add a cpp function to the swim file
        :param return_type: the return type of the function
        :param function_name: the name of the function. Note: the name will be mutated to ensure no collisions,\
        the true name of the function will be returned.
        :param lines: the code lines of the function
        :param arguments: a list of cpp parameter identifiers for the function
        :param add_scope: the scope of the function deceleration.
        :param name_abs: if set, regular name mangling will be ignored the function's identifier will be identical
            to function_name. note that this identifier will not be stored in the swim's translated_ids.
        :return: the true identifier of the function.
        """
        if name_abs:
            name = function_name
        else:
            name = self.create_unique_id(function_name)
        frag_str = (',fragment="' + ','.join(fragments) + '"') if fragments else ''
        lines = clean_source(lines)
        lines = [
            '%fragment ("' + name + '","header"' + frag_str + '){',
            return_type + ' ' + name + '(' + ', '.join(arguments) + ') {',
            *('\t' + l for l in lines),
            '}',
            '}'
        ]
        add_scope(self, lines)
        return name

    def add_nl(self, n=1):
        """
        add a blank line. Note: the blank line will be ignored if the swim's verbosity is at Verbosity.Critical or lower
        :param n: the number of blank lines to add.
        :return:  the nuber of lines added.
        """
        if self.verbosity <= Verbosity.critical:
            return 0
        if n == 1:
            self.lines.append('')
        else:
            self.lines.extend('' for _ in range(n))
        return n

    def __str__(self):
        if self.module_name:
            return f'swim for module {self.module_name}'
        return super().__str__()

    def __iter__(self):
        """
        Get an iterable of the lines stored in the swimport.
        """
        return (yield from self.lines)

    def write(self, dst: Union[str, PathLike, TextIO]):
        """
        write the lines of the swim to a file or path
        """
        if isinstance(dst, (str, PathLike)):
            dst = open(fspath(dst), 'w')
            own = True
        else:
            own = False

        dst.writelines(
            it.chain.from_iterable(zip(self, it.repeat('\n')))
        )

        if own:
            dst.close()

    @staticmethod
    def _normalize_to_cpp_type(t)->str:
        if isinstance(t, str):
            return t
        type_dict = {
            int: 'int',
            float: 'double',
            bool: 'bool',
            str: 'std::string',
        }
        ret = type_dict.get(t)
        if ret:
            return ret
        if isinstance(t, tuple):
            return 'std::tuple<' + ', '.join(Swim._normalize_to_cpp_type(i) for i in t) + '>'
        if isinstance(t, list) and len(t) == 1:
            return 'std::vector<' + Swim._normalize_to_cpp_type(t[0]) + '>'
        if isinstance(t, set) and len(t) == 1:
            return 'std::unordered_set<' + Swim._normalize_to_cpp_type(next(iter(t))) + '>'
        if isinstance(t, dict) and len(t) == 1:
            k, v = next(iter(t.items()))
            return 'std::unordered_map<' + Swim._normalize_to_cpp_type(k) + ', ' + Swim._normalize_to_cpp_type(v) + '>'
        raise ValueError(f"can't parse as c++ type: {t}")

    def get_porting(self, type_: Union[str, TypeSwimporting, Tuple[str, TypeSwimporting]]) -> Tuple[str, TypeSwimporting]:
        if isinstance(type_, tuple) and len(type_) == 2\
                and isinstance(type_[0], str) and isinstance(type_[1], TypeSwimporting):
            return type_
        if isinstance(type_, TypeSwimporting):
            return type_.cpp_name, type_
        try:
            type_ = self._normalize_to_cpp_type(type_)
            return type_, self.types[type_]
        except KeyError as e:
            raise LookupError(f'type {type_} has not been swimported (did you remember to use pools.primitive?)') from e
