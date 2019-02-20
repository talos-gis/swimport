from typing import Iterator, Dict, Iterable

import re

from swimport.swim import Swim
from swimport.__util__ import *
from swimport.model import Swimporting, SwimportAggregate, Typedef, CPPObject, Compileable, object_swimporting


class TypedefAggregate(Iterable[Swimporting], SwimportAggregate):
    """
    An object that acts like a swim. But accepts only typedef swimportings.
    It can then be iterated to sort the swimported typedefs topologically.
    >>> ta = TypedefAggregate()
    >>> class Mock_Swimporting: pass
    >>> def ap(d, s):
    ...     app = Mock_Swimporting()
    ...     app.object = Typedef.make(str(d), str(s))
    ...     ta(app)
    >>> ap(0, 1)
    >>> ap(2, 3)
    >>> ap(1, 2)
    >>> list((t.object.dest_type, t.object.source_type) for t in ta)
    [('2', '3'), ('1', '2'), ('0', '1')]
    """

    def __init__(self):
        self.imported_typedefs: Dict[Typedef, Swimporting] = {}

    def apply_porting(self, swimporting: Swimporting):
        """
        store a swimporting of a typedef
        :param swimporting: the swimporting object
        :return: whether the object was successfully imported (returns 0 if the typedef wal already imported)
        :raises TypeError: if swimporting is not an ObjectSwimporting[Typedef]
        """
        obj: CPPObject = getattr(swimporting, 'object', None)
        if not isinstance(obj, Typedef):
            raise TypeError('Typedef aggregate can only accept swimportings of typedefs')
        v = self.imported_typedefs.setdefault(obj, swimporting)
        if v is swimporting:
            return obj.name
        return 0

    def __iter__(self) -> Iterator[Swimporting]:
        """
        :return: all the swimportings stored in the aggregate in topological order
        """
        mapping: Dict[str, Swimporting] = {k.dest_type: v for k, v in self.imported_typedefs.items()}
        while mapping:
            _, td = mapping.popitem()
            stack = [td]
            while td.object.source_type in mapping:
                td = mapping.pop(td.object.source_type)
                stack.append(td)
            yield from reversed(stack)


class TypedefSourceTrigger(Typedef.Trigger):
    """A trigger for typedefs. See type_matching for an explanation on type pattern matching"""

    def __init__(self, pattern: Compileable):
        self.pattern = re.compile(pattern)

    def is_valid(self, rule: 'SwimRule', obj):
        return super().is_valid(rule, obj)\
            and self.pattern.fullmatch(obj.normalized_type)


@Typedef.set_default_trigger
class TypedefDestinationTrigger(Typedef.Trigger):
    """A trigger for typedefs"""

    def __init__(self, destination_type_pattern: Compileable):
        """
        :param destination_type_pattern: pattern the destination type (the new type) must fully match to be valuid
        """
        self.destination_type_pattern = re.compile(destination_type_pattern)

    def is_valid(self, rule, obj: Typedef):
        return super().is_valid(rule, obj) \
               and self.destination_type_pattern.fullmatch(obj.dest_type)


@Typedef.set_default_behaviour
class TypedefBehaviour(Typedef.Behaviour):
    DEFAULT_MAPS = ('{} &OUTPUT', '{} *OUTPUT',
                    '{} &INPUT', '{} *INPUT',
                    '{} &INOUT', '{} *INOUT',
                    '{} const *INPUT', '{} const &INPUT',
                    '({}* ARGOUTVIEW_ARRAY1, size_t* DIM1)')
    """A behaviour for typedefs"""

    def __init__(self, maps=DEFAULT_MAPS, inline=False, no_declare=False):
        """
        :param maps: the typemaps to apply to the new type. default is both OUTPUT and ARR_OUT
        :param inline: whether to inline the typedef's declaration
        :param no_declare: whether to forgo declaring the typedef entirely (leaving only the maps)
        """
        self.maps = list(maps)
        self.inline = inline
        self.no_declare = no_declare

    @object_swimporting
    def wrap(self, rule, obj: Typedef, swim):
        mappings = []
        mappings.extend(
            '%apply ' + m.format(obj.source_type) + ' {' + m.format(obj.dest_type) + '};'
            for m in self.maps
        )
        if self.inline:
            body_scope = Swim.add_inline
        elif self.no_declare:
            body_scope = None
        else:
            body_scope = Swim.add_raw

        swim.add_comment(f'typedef {obj.source_type} {obj.dest_type};')
        swim.add_comment(f'rule used: {rule}', verbosity_level=Verbosity.debug)
        swim.add_raw(mappings)
        if body_scope:
            body_scope(swim, f'typedef {obj.source_type} {obj.dest_type};')
        swim.add_nl()

        if swim.types.get(obj.dest_type):
            raise Exception('the destination type of the typedef ('+obj.dest_type+') was previously imported.')
        src_porting = swim.types.get(obj.source_type)
        if src_porting:
            swim.types[obj.dest_type] = src_porting
