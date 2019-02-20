from __future__ import annotations

from typing import Callable, Type, Optional, Union, Pattern, Iterable, Any, TYPE_CHECKING, Set

from abc import ABC, abstractmethod
import re
from itertools import chain
from functools import partial

if TYPE_CHECKING:
    from swimport.model.cpp_object import Source, CPPObject

from swimport.__util__ import Replaceable

Swimporting = Callable[[Any], bool]


def object_swimporting(func: Callable[['Behaviour', 'SwimRule', Any, Any], Swimporting]) \
        -> Callable[['SwimRule', Any], Swimporting]:
    """
    a method wrapper that parts a function's last swim parameter, amking it create a delayed swimporting instead
    of running the function. The wrapped function also checks that the swim object hasn't imported the cpp object already.
    the wrapped function can also called normally as declared.
    """

    def ret(self, rule, obj, swim=...):
        def ret(swim):
            if obj in swim.imported:
                return False
            ret = func(self, rule, obj, swim)
            if ret or ret is None:
                swim.imported[obj] = rule
                return True
            return False

        if swim is not ...:
            return ret(swim)
        ret.object = obj
        ret.rule = rule
        return ret

    return ret


class Trigger(ABC, Replaceable):
    """An abstract class to decide whether a cpp object should be imported"""

    @abstractmethod
    def is_valid(self, rule, obj) -> bool:
        """get whether an object, under a specific rule, should be imported"""
        return True

    def __and__(self, other):
        """Create a trigger that only accepts values that both triggers accept"""
        return AndTrigger(self, other)

    def __or__(self, other):
        """Create a trigger that only accepts values that either triggers accept"""
        return OrTrigger(self, other)

    def __xor__(self, other):
        """Create a trigger that only accepts values that one of triggers accept, but not the other"""
        return XorTrigger(self, other)

    def __invert__(self):
        """Create a trigger that only accepts values that self does not"""
        return NotAnyTrigger(self)

    def __gt__(self, other):
        """Create a trigger that only accepts values that self accepts but other does not"""
        return GtTrigger(self, other)


class CategorizedTrigger(Trigger):
    """A custom trigger that only accept objects of a specific kind"""
    object_category: Type

    def is_valid(self, rule: 'SwimRule', obj):
        return super().is_valid(rule, obj) and isinstance(obj, self.object_category)

    def __init_subclass__(cls, *, specialization, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.object_category = specialization


Compileable = Union[str, Pattern[str]]


class NameTrigger(Trigger):
    """A trigger that only allows objects whose name fully matches the pattern"""

    def __init__(self, pattern: Compileable):
        self.name_pattern = re.compile(pattern)

    def is_valid(self, rule: 'SwimRule', obj):
        return super().is_valid(rule, obj) and self.name_pattern.fullmatch(obj.name)


class AggregateTrigger(Trigger):
    """A trigger that aggregates results of other sub-triggers"""

    def __init__(self, aggregate: Callable[[Iterable[bool]], bool], *triggers: Trigger):
        self.aggregate = aggregate
        self.sub_triggers = []
        if not triggers:
            raise ValueError('at least one trigger must be presented')
        object_category = ...
        for sub_trigger in triggers:
            if object_category:
                oc = getattr(sub_trigger, 'object_category', None)
                if object_category in (oc, ...):
                    object_category = oc
                else:
                    object_category = False

            # check if we can flatten another aggregate ((a|b)|(c|d)) -> (a|b|c|d)
            if isinstance(sub_trigger, AggregateTrigger) and sub_trigger.aggregate is self.aggregate:
                self.sub_triggers.extend(sub_trigger.sub_triggers)
            else:
                self.sub_triggers.append(sub_trigger)

        if object_category:
            self.object_category = object_category

    def is_valid(self, rule: 'SwimRule', obj):
        return self.aggregate(t.is_valid(rule, obj) for t in self.sub_triggers)


AndTrigger = partial(AggregateTrigger, all)
OrTrigger = partial(AggregateTrigger, any)
XorTrigger = partial(AggregateTrigger, lambda a: sum(map(bool, a)) % 2 == 1)
NotAnyTrigger = partial(AggregateTrigger, lambda a: not any(a))
GtTrigger = partial(AggregateTrigger, lambda i: bool(next(i)) > bool(next(i)))


class SwimRule(ABC):
    """A rule for swimporting"""

    @abstractmethod
    def do(self, obj) -> Optional[Swimporting]:
        """Get a swimporting for a cppobject, or None if the object does not pass the trigger"""
        pass

    def __call__(self, *sources: Source) -> Iterable[Swimporting]:
        """Get swimportings for all valid objects in sources"""
        if len(sources) > 1:
            src = chain.from_iterable(sources)
        elif sources:
            src = sources[0]
        else:
            return

        for o in src:
            s = self.do(o)
            if s:
                yield s


class Behaviour(SwimRule, Replaceable):
    """An abstract class to wrap objects to import in swimportings"""

    rule_cls: Type[TriggerBehaviourSwimRule]  # the type of rule to create when >> is used

    @abstractmethod
    def wrap(self, rule: SwimRule, obj) -> Swimporting:
        pass

    def default_is_valid(self, rule: 'SwimRule', obj) -> bool:
        return True

    def do(self, obj):
        if not self.default_is_valid(self, obj):
            return None
        return self.wrap(self, obj)

    def __rrshift__(self, other) -> 'TriggerBehaviourSwimRule':
        return self.rule_cls(other, self)


class CategorizedBehaviour(Behaviour):
    """A custom trigger to wrap objects of a specific kind. This class doesn't behave in any way special,
    but sets its inheritor's object_category so they can be used with categorised triggers"""
    object_category: Type[CPPObject]

    @abstractmethod
    def wrap(self, rule: 'SwimRule', obj) -> Swimporting:
        pass

    def default_is_valid(self, rule: 'SwimRule', obj):
        return super().default_is_valid(rule, obj) \
               and isinstance(obj, self.object_category)

    def __rrshift__(self, other):
        if (other is not ...) and (not isinstance(other, Trigger)):
            other = self.object_category.Trigger(other)
        return super().__rrshift__(other)

    def __init_subclass__(cls, *, specialization, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.object_category = specialization


class TriggerBehaviourSwimRule(SwimRule, Replaceable):
    """A rule for swimporting specific objects"""

    def __init__(self, trigger: Trigger, behaviour: Behaviour, name=None):
        """
        constructor
        :param trigger: the trigger of the rule, ... to accept any object
        :param behaviour: the behaviour to use
        :param name: the name of the rule (optional)
        """
        self.trigger = trigger
        self.behaviour = behaviour
        self.name = name
        t_category = getattr(self.trigger, 'object_category', None)
        b_category = getattr(self.behaviour, 'object_category', None)
        if t_category is not b_category \
                and self.trigger is not ...:
            raise ValueError(
                f'trigger and behaviour category mismatch: {t_category}(trigger) vs {b_category}(behaviour)')
        self.category = t_category

    def __str__(self):
        if self.category:
            if self.name:
                return f'{self.category.__name__} rule: {self.name}'
            return f'unnamed {self.category.__name__} rule'
        if self.name:
            return f'rule: {self.name}'
        return super().__str__()

    def do(self, obj) -> Optional[Swimporting]:
        """Get a swimporting for a cppobject, or None if the object does not pass the trigger"""
        if self.trigger is ...:
            valid = self.behaviour.default_is_valid(self, obj)
        else:
            valid = self.trigger.is_valid(self, obj)

        if valid:
            return self.behaviour.wrap(self, obj)
        return None


Behaviour.rule_cls = TriggerBehaviourSwimRule

class SwimportingsResult:
    """A result for importing multiple swimportings."""

    def __init__(self):
        self.value = 0
        self.names: Set[str] = set()

    def __iadd__(self, other):
        if isinstance(other, int):
            self.value += other
        elif isinstance(other, str):
            self.names.add(other)
            self.value += 1
        elif isinstance(other, Iterable):
            prev_len = len(self.names)
            self.names.update(other)
            self.value += (len(self.names) - prev_len)
        elif isinstance(other, SwimportingsResult):
            anon = other.value - len(other.names)
            prev_len = len(self.names)
            self.names.update(other.names)
            self.value += (len(self.names) - prev_len) + anon
        else:
            return NotImplemented
        return self

    def __bool__(self):
        return bool(self.value)

    def __eq__(self, other):
        return self.value == other \
               or (isinstance(other, type(self)) and other.value == self.value and other.names == self.names)

    def __ne__(self, other):
        return self.value != other \
               and (not isinstance(other, type(self)) or other.value != self.value or other.names != self.names)

    def __lt__(self, other):
        return self.value < other

    def __le__(self, other):
        return self.value <= other

    def __gt__(self, other):
        return self.value > other

    def __ge__(self, other):
        return self.value >= other

    def __contains__(self, item):
        return item in self.names

    def __int__(self):
        return self.value

    def __iter__(self):
        return (yield from self.names)


class SwimportAggregate(ABC):
    @abstractmethod
    def apply_porting(self, swimporting: Swimporting) -> Union[str, int]:
        """
        Apply a single porting to the swim
        :returns: whether or not the porting succeeded
        """

    def apply_portings(self, portings: Iterable[Swimporting]) -> SwimportingsResult:
        """
        apply multiple swimportings
        :return: a SwimportResult object
        """
        ret = SwimportingsResult()
        for p in portings:
            ret += self.apply_porting(p)
        return ret

    def __call__(self, arg) -> SwimportingsResult:
        """apply either a single or multiple swimportings"""
        if not isinstance(arg, Iterable):
            arg = arg,
        return self.apply_portings(arg)
