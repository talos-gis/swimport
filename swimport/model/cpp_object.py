from __future__ import annotations

from typing import Callable, Type, Any, Generic, Optional, TypeVar, List, Iterable

from abc import ABC, abstractmethod
from inspect import isabstract
from functools import update_wrapper, lru_cache
import re
from enum import Enum
from itertools import chain

import swimport.model.rules as rules_mod

import CppHeaderParser

T = TypeVar('T')

Source = Iterable['CPPObject']


class HeaderSource(Source):
    def __init__(self, header, lines):
        self._objects: List[CPPObject] = [
            *(Function(f, lines) for f in header.functions),  # methods
            *(Typedef(pair) for pair in header.typedefs.items()),  # typedefs
            *(Enumeration(e, lines) for e in header.enums),  # enums
            *(Variable(v) for v in header.variables),  # vars
            *(Container(c, lines) for c in header.classes.values())  # containers
        ]

    def __iter__(self):
        yield from self._objects


class FileSource(HeaderSource):
    """A source from a cpp header file. Reads the header file and generates CPPObject wrappers for the objects
    detected."""

    def __init__(self, source_path, directives=()):
        self.source_path = source_path
        self.directives = directives

        with open(self.source_path) as r:
            lines = [l.rstrip() for l in r]
        header = CppHeaderParser.CppHeader('\n'.join(lines), 'string')  # self.source_path, 'file')
        super().__init__(header, lines)


class RawSource(HeaderSource):
    """A source from a string"""

    def __init__(self, source_string: str):
        self.src_string = source_string

        lines = self.src_string.splitlines(False)
        header = CppHeaderParser.CppHeader(self.src_string, 'string')  # self.source_path, 'file')
        super().__init__(header, lines)


class CategorizedSurrogate(Generic[T]):
    """
    A class that holds 2 classes, one for inheriting, one for creating
    """

    def __init__(self, type_, inherit_class: Type[T]):
        self._callable: Optional[Callable[..., T]] = None
        self.owner = type_

        class InheritCls(inherit_class, specialization=type_):
            def __init_subclass__(cls, **kwargs):
                super().__init_subclass__(specialization=cls.object_category, **kwargs)

        self.inherit_cls: Type[T] = InheritCls

    def __mro_entries__(self, bases):
        return self.inherit_cls,

    def __call__(self, *args, **kwargs):
        if not self._callable:
            raise TypeError(f'this superclass surrogate is not callable'
                            f' (did you mean {self.owner.__name__}.set_default?)')
        if len(args) == 1 and not kwargs and isinstance(args[0], self):
            return args[0]
        return self._callable(*args, **kwargs)

    def __instancecheck__(self, instance):
        return isinstance(instance, self.inherit_cls)

    def __subclasscheck__(self, subclass):
        return issubclass(self, self.inherit_cls)

    @property
    def callable(self):
        return self._callable

    @callable.setter
    def callable(self, v):
        self._callable = v
        update_wrapper(self, v, assigned=('__doc__',))


class CPPObject(ABC):
    """base class for all cpp objects that can be imported"""
    Behaviour: Type['rules_mod.Behaviour']
    Trigger: Type['rules_mod.Trigger']

    @classmethod
    def set_default_behaviour(cls, func: Callable[..., 'Behaviour']):
        cls.Behaviour.callable = func
        return func

    @classmethod
    def set_default_trigger(cls, func: Callable[[Any], 'Trigger']):
        cls.Trigger.callable = func
        return func

    def __init__(self, data):
        if isinstance(data, type(self)):
            self.__init__(data._data)
        else:
            self._data = data

    @property
    @abstractmethod
    def name(self) -> str:
        """identifiable name of the object"""
        pass

    @property
    @abstractmethod
    def body(self) -> str:
        """body of the object's declaration"""
        pass

    def __repr__(self):
        return f'interface wrapper for {type(self).__name__} {self.name}'

    def __str__(self):
        return self.name

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not isabstract(cls):
            cls.Behaviour = CategorizedSurrogate(cls, rules_mod.CategorizedBehaviour)
            cls.Trigger = CategorizedSurrogate(cls, rules_mod.CategorizedTrigger)


class _Sourced(CPPObject):
    """a cpp object that also holds a reference to its own source deceleration"""

    def __init__(self, data, lines):
        super().__init__(data)
        self.source_lines = lines


class _Declaration(_Sourced):
    """a cpp object whose declarations are a single line"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._body = None

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    def body(self) -> str:
        if self._body is None:
            ind = self._data['line_number'] - 1
            ret = [self.source_lines[ind]]
            while not ret[-1].endswith(';'):
                ind += 1
                ret.append(self.source_lines[ind])
            self._body = ' '.join(r.strip() for r in ret)
        return self._body


class _Scope(_Sourced):
    """cpp object whose declarations are an entire scope"""

    @staticmethod
    def _delve(depth, maxdepth, newline):
        while newline:
            opener_index = newline.find('{')
            closer_index = newline.find('}')

            if opener_index == -1:
                if closer_index == -1:
                    break
                depth -= 1
                newline = newline[closer_index + 1:]
                continue

            if closer_index == -1 or opener_index < closer_index:
                depth += 1
                if depth > maxdepth:
                    maxdepth = depth
                newline = newline[opener_index + 1:]
                continue

            depth -= 1
            newline = newline[closer_index + 1:]
            continue
        return depth, maxdepth

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    def body(self) -> str:
        ret = []
        depth = 0
        max_depth = 0
        ind = self._data['line_number'] - 1
        while not (max_depth > 0 and depth == 0):
            ret.append(self.source_lines[ind])
            ind += 1
            depth, max_depth = self._delve(depth, max_depth, ret[-1])
        return '\n'.join(ret)


class _TypedCPPObject(CPPObject):
    """
    A cpp object that is associated with a distinct type
    """

    @property
    @abstractmethod
    def type(self) -> str:
        pass

    @property
    def normalized_type(self):
        return normalize_type(self.type)


class Function(_Declaration, _TypedCPPObject):
    """a cpp method"""

    class Param(_TypedCPPObject):
        """a function parameter, this object cannot be swimported directly"""

        def __init__(self, data, owner=None, index=None):
            super().__init__(data)
            self.owner = owner
            self.index = index

        @classmethod
        def make(cls, name, type_, default=None, **kwargs):
            data = {
                'name': name,
                'type': type_,
                'defaultValue': default
            }
            return cls(data, **kwargs)

        @property
        def name(self) -> str:
            return self._data['name']

        @property
        def type(self) -> str:
            return self._data['type']

        @property
        def default(self):
            return self._data.get('defaultValue', None)

        @property
        def body(self):
            ret = self.sign
            default = self.default
            if default:
                ret += ' = ' + default
            return ret

        @property
        def next(self) -> 'Function.Param':
            return self.owner.parameters[self.index + 1]

        @property
        def next_or_none(self) -> Optional['Function.Param']:
            try:
                return self.next
            except IndexError:
                return None

        @property
        def sign(self) -> str:
            return self.type + ' ' + self.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params = [self.Param(p, owner=self, index=i) for (i, p) in enumerate(self._data['parameters'])]

    @classmethod
    def make(cls, name, params, rtnType):
        data = {
            'name': name,
            'rtnType': rtnType,
            'parameters': params,
        }
        ret = cls(data, None)
        ret._body = ret.sign + ';'
        return ret

    @property
    def name(self) -> str:
        return self._data['name']

    @property
    def parameters(self) -> List[Param]:
        return self.params

    @property
    def return_type(self) -> str:
        return self._data['rtnType']

    @property
    def prm_types(self):
        return (p.type for p in self.parameters)

    @property
    def prm_names(self):
        return (p.name for p in self.parameters)

    @property
    def pattern(self):
        return self.name + '(' + ', '.join(f'{p.type} {p.name}' for p in self.parameters) + ')'

    @property
    def sign(self):
        return self.return_type + ' ' + self.name + '(' + ', '.join(p.body for p in self.parameters) + ')'

    @property
    def type(self):
        return self.return_type


class Typedef(_TypedCPPObject):
    """a cpp typedef"""

    @classmethod
    def make(cls, new_type, old_type):
        return cls((new_type, old_type))

    @property
    def dest_type(self) -> str:
        return self._data[0]

    @property
    def source_type(self) -> str:
        return self._data[1]

    @property
    def body(self) -> str:
        return f'typedef {self.source_type} {self.dest_type};'

    @property
    def name(self):
        return self.dest_type

    @property
    def type(self):
        return self.source_type


class Variable(_TypedCPPObject):
    """a cpp variable"""

    const_pattern = re.compile('(?<![a-zA-Z0-9_])const(?![a-zA-Z0-9_])')

    @property
    def name(self):
        return self._data['name']

    @property
    def type(self):
        return self._data['type']

    @property
    def isextern(self):
        return self._data['extern']

    @property
    def body(self):
        preamble = []
        if self.isextern:
            preamble.append('extern')
        preamble = ' '.join(preamble)
        if preamble:
            preamble += ' '
        return preamble + self.type + ' ' + self.name + ';'


class Container(_Scope):
    """a container (class, struct, or union)"""

    def __init__(self, data, source_lines):
        if data['name'].startswith('union '):  # get rid of union header for unions
            data['name'] = data['name'][len('union '):]
        super().__init__(data, source_lines)

        self.methods = list(chain.from_iterable(
            (self.Method(m, source_lines, access=k) for m in v)
            for k, v in self._data['methods'].items()))

        self.members = list(chain.from_iterable(
            (self.Member(m, access=k, owner=self) for m in v)
            for k, v in self._data['properties'].items()))

    class Kind(Enum):
        Union = 'union'
        Class = 'class'
        Struct = 'struct'

    class Member(Variable):
        """a member of a container"""

        def __init__(self, *args, access, owner: Container):
            super().__init__(*args)
            self.access = access
            self.owner = owner

        @property
        def is_static(self):
            return bool(self._data['static'])

    class Method(Function):
        def __init__(self, *args, access):
            super().__init__(*args)
            self.access = access

        @property
        def is_static(self):
            return bool(self._data['static'])

    @property
    def name(self):
        return self._data['name']

    @property
    def kind(self) -> Kind:
        return self.Kind[self._data['declaration_method'].capitalize()]

    @property
    def public_bases(self)->Iterable[str]:
        yield from (i['class'] for i in self._data['inherits'] if i['access'] == 'public')


class Enumeration(_Declaration, _TypedCPPObject):
    """a cpp enum"""

    class EnumerationValue(CPPObject):
        """A value in a cpp enum"""

        @property
        def name(self):
            return self._data['name']

        @property
        def value(self):
            return self._data['value']

        @property
        def body(self):
            return self.name + ' = ' + str(self.value)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.members = [self.EnumerationValue(m) for m in self._data['values']]

    @property
    def name(self):
        return self._data['name']

    @property
    def type(self) -> str:
        ret = self._data['type']
        if not ret:
            return 'int'
        return getattr(ret, '__name__', ret)


idempotent_qualifiers = frozenset(('const', 'volatile', 'mutable'))
prefix_qualifiers = ('const', 'volatile', 'mutable')
prefix_pattern = re.compile('^(' + '|'.join(
    (re.escape(q) + (r'(?![a-zA-Z0-9_])' if q[-1].isalnum() else ''))
    for q in prefix_qualifiers) + ')')
postfix_qualifiers = ('const', 'volatile', 'mutable', '*', '&&', '&')
postfix_pattern = re.compile('(' + '|'.join(
    ((r'(?<![a-zA-Z0-9_])' if q[0].isalnum() else '') + re.escape(q))
    for q in postfix_qualifiers) + ')$')


@lru_cache()
def normalize_type(type_str: str):
    """
    Normalizes a c++ type string in the following ways:
    * qualifiers are gathered and are always ordered right-to-left, space separated
        (const int *  -> int const *)
    * primitive type name are normalized to their simplest versions:
        (signed short int -> short)
    * const, volatile, and mutable qualifiers are bunched, and sorted alphabetically
        (volatile const mutable const volatile int -> int const mutable volatile)

    >>> normalize_type('int')
    'int'
    >>> normalize_type('const int')
    'int const'
    >>> normalize_type('int const *')
    'int const *'
    >>> normalize_type('   char const*    ')
    'char const *'
    >>> normalize_type('const wchar_t &const*')
    'wchar_t const & const *'
    >>> normalize_type('signed   long            long   int')
    'long long'
    >>> normalize_type('signed short    int')
    'short'
    >>> normalize_type('unsigned short    int')
    'unsigned short'
    >>> normalize_type('int&& const')
    'int && const'
    >>> normalize_type('const short int*&')
    'short const * &'
    >>> normalize_type('long      double')
    'long double'
    >>> normalize_type('const char * const volatile')
    'char const * const volatile'
    >>> normalize_type('char * volatile const')
    'char * const volatile'
    >>> normalize_type('char * const volatile const')
    'char * const volatile'
    >>> normalize_type('const char const const const *')
    'char const *'
    >>> normalize_type('char**')
    'char * *'
    >>> normalize_type('const constintvolatile*&')
    'constintvolatile const * &'
    >>> normalize_type('volatile const mutable const volatile int')
    'int const mutable volatile'
    >>> normalize_type('int*const&volatile*const&&const**')
    'int * const & volatile * const && const * *'
    """
    stack = []
    type_str = type_str.strip()
    # gather the components
    while True:
        match = postfix_pattern.search(type_str) or prefix_pattern.match(type_str)
        if not match:
            break
        kw = match.group(1)
        stack.append(kw)
        if match.re is postfix_pattern:
            type_str = type_str[:-len(kw)].rstrip()
        else:  # match.re is cls.prefix_pattern
            type_str = type_str[len(kw):].lstrip()

    # at this point, type_str holds the primitive name (int, long int, unsigned short,...)
    # we need to normalize it
    type_str = re.sub(r'\s{2,}', ' ', type_str.strip())
    if type_str in ('signed', 'unsigned'):
        type_str += ' int'

    if type_str.startswith('signed ') \
            and any(type_str.endswith(' ' + pi) for pi in ('int', 'short', 'long')):
        type_str = type_str[len('signed '):]

    for actual_type in ('short', 'long', 'long long'):
        if type_str.endswith(' ' + actual_type + ' int') \
                or type_str == actual_type + ' int':
            type_str = type_str[:-len(' int')]
            break

    # now type_str holds the normalized primitive type, add qualifiers to it
    ret = [type_str]

    # all the idempotent, order invariant qualifiers for the current symbol (const, volatile...)
    idempotent_qualifier_subset = set()

    for qualifier in reversed(stack):
        if qualifier in idempotent_qualifier_subset:
            continue  # const const -> const
        if qualifier in idempotent_qualifiers:
            idempotent_qualifier_subset.add(qualifier)
        else:
            for q in sorted(idempotent_qualifier_subset):
                ret.append(q)
            idempotent_qualifier_subset.clear()
            ret.append(qualifier)
    for q in sorted(idempotent_qualifier_subset):
        ret.append(q)
    return ' '.join(ret)
