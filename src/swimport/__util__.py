from __future__ import annotations
from typing import Iterable, Optional, Union, TypeVar, Sequence

import re
from enum import IntEnum
from functools import lru_cache, partial, update_wrapper
from string import Formatter
from textwrap import dedent
from itertools import chain
from inspect import Parameter, signature

T = TypeVar('T')


class Verbosity(IntEnum):
    """verbosity of the output file"""
    none = 0
    critical = 1
    info = 2
    debug = 3


def clean_source(source) -> Sequence[str]:
    """
    converts string-like objects to a sequence of strings. includes stripping, and dedenting
    >>> clean_source("\\n\\ta\\n\\tb\\n\\tc")
    ['a', 'b', 'c']
    >>> clean_source("\\ta\\n\\tb\\n\\tc\\n")
    ['a', 'b', 'c']
    """
    if isinstance(source, str):
        return dedent(source).strip().splitlines(keepends=False)
    if isinstance(source, Sequence):
        return source
    if isinstance(source, Iterable):
        return list(source)
    if type(source).__str__ is not object.__str__:
        return clean_source(str(source))
    raise TypeError(f'object {source} cannot be interpreted as string or lines')


def scope_lines(lines, start: Optional[str], end: Optional[str], indent: Optional[str] = '\t',
                inline: Union[bool, type(...)] = ..., inline_sep: Optional[str] = None):
    """
    wraps lines in a scope, and returns the lines as a list
    :param lines: the lines (or string-like, ran through clean_source)
    :param start: the opener of the scope
    :param end: the closer of the scope
    :param indent: the indentation to apply to each line of the scope
    :param inline: whether to inline the scope. or ... to only inline if the source is in a single line.
    :param inline_sep: the separator to use when joining multiple lines in an inlined scope.
    :return: a list of the scope lines
    """
    lines = clean_source(lines)
    if not lines:
        return []

    if inline is ...:
        inline = len(lines) == 1

    if inline:
        if len(lines) == 1:
            s = lines[0]
        else:
            if inline_sep is None:
                raise ValueError('seperator must be entered for multiline, inlined scope')
            s = inline_sep.join(lines)
        start = '' if not start else start + ' '
        end = '' if not end else ' ' + end
        return [start + s + end]

    if not (start or end or indent):
        return lines

    ret = []

    if start:
        ret.append(start)

    if indent:
        lines = (indent + l for l in lines)

    ret.extend(lines)

    if end:
        ret.append(end)

    return ret


id_trans_table = {
    '<': '_lt',
    '>': '_gt',
    ':': '_col_',
    '*': '_star_',
    '&': '_ref_',
    '.': '_dot_'
}
id_sub_pattern = re.compile(r'(^(?![^a-zA-Z_]))|[^a-zA-Z0-9_]')


@lru_cache()
def clean_identifier(unsafe):
    """
    turns an unsafe string or object into a safe cpp identifier
    (without illegal characters, whitespace, and starting with a legal character)
    """
    if not isinstance(unsafe, str):
        if isinstance(unsafe, Iterable):
            return '_'.join(clean_identifier(i) for i in unsafe)
        unsafe = str(unsafe)

    def sub_func(match):
        return id_trans_table.get(match[0], '_')

    return id_sub_pattern.sub(sub_func, unsafe)


class ExtendedFormatter(Formatter):
    """
    Formatter with extended conversion symbols:
    * l: lowercase
    * u: uppercase
    * c: capitalized
    """

    def convert_field(self, value, conversion):
        if conversion == 'u':
            return str(value).upper()
        elif conversion == 'l':
            return str(value).lower()
        elif conversion == 'c':
            return str(value).capitalize()
        return super().convert_field(value, conversion)


Self_Replaceable = TypeVar('Self_Replaceable', bound='Replaceable')


class Replaceable:
    """
    A base class to allow for easy copying of simple types
    NOTE: this should only be used with immutable types
    """

    def __new__(cls, *args, **kwargs):
        ret = super().__new__(cls)
        ret.__args = (args, kwargs)
        return ret

    @property
    def can_replace(self):
        return True

    def replace(self: Self_Replaceable, **changes) -> Self_Replaceable:
        """
        create a new object of the type of self, using self's arguments as template
        :param kwargs: initialization arguments to change
        :return: a new instance of self's type, using a mix of self's init arguments and kwargs
        """
        if not self.can_replace:
            raise Exception(f'object of type {type(self)} is in a non-replaceable state')

        if not changes:
            return self

        args = list(self.__args[0])
        kwargs = dict(self.__args[1])
        for k, v in changes.items():
            param_index = self.__init_params.get(k, -1)
            if 0 <= param_index < len(args):
                args[param_index] = v
            else:
                kwargs[k] = v
        return type(self)(*args, **kwargs)

    def __init_subclass__(cls, **kwargs):
        # to allow kwargs->args replacement, we need a dict of all of the class's original positional arguments
        super().__init_subclass__(**kwargs)
        update_wrapper(cls.replace, cls.__init__)
        try:
            parent_params = cls.__init_params
        except AttributeError:
            parent_params = {}

        cls.__init_params = {}
        for i, p in enumerate(signature(cls.__init__).parameters.values()):
            if p.kind == Parameter.VAR_POSITIONAL:
                for n, j in parent_params.items():
                    cls.__init_params[n] = j + i - 1

            if p.kind not in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.POSITIONAL_ONLY):
                break

            cls.__init_params[p.name] = i - 1

    # all the other methods here are rudimentary but they're useful to have
    def __repr__(self):
        args = chain(
            (repr(a) for a in self.__args[0]),
            (str(k) + ' = ' + repr(v) for k, v in self.__args[1].items())
        )
        return type(self).__name__ + '(' + ', '.join(args) + ')'

    def __eq__(self, other):
        return super().__eq__(self, other) \
               or (self.can_replace and isinstance(other, type(self)) and other.can_replace and
                   (self.__args == other.__args))

    def __hash__(self):
        return hash(
            (type(self), self.__args[0], tuple(self.__args[1].items()))
        )


__all__ = [
    'Verbosity',
    'scope_lines', 'clean_source', 'clean_identifier',
    'ExtendedFormatter',
    'Replaceable'
]
