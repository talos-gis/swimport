from typing import Container

from abc import abstractmethod
from functools import reduce
from operator import or_


class Filter(Container[int]):
    @abstractmethod
    def __contains__(self, item: int):
        pass

    def __sub__(self, other):
        return SubFilter(self, other)

    def __or__(self, other):
        return AddFilter(self, other)

    def __and__(self, other):
        return MulFilter(self, other)


class AllFilter(Filter):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        if isinstance(item, int):
            return ConstFilter(item)
        if isinstance(item, slice):
            return SliceFilter(item)
        return reduce(or_,
                      (self[i] for i in item))

    def __repr__(self):
        return 'All'


All = AllFilter()


class EmptyFilter(Filter):
    def __contains__(self, item):
        return False

    def __repr__(self):
        return 'Empty'


Empty = EmptyFilter()


class ConstFilter(Filter):
    def __init__(self, c):
        self.c = c

    def __contains__(self, item):
        return item == self.c


class SliceFilter(Filter):
    def __init__(self, slice_):
        self.start = slice_.start or 0
        self.end = slice_.stop or float('inf')
        self.step = slice_.step

    def __contains__(self, item):
        if (item < self.start) or (item >= self.end):
            return False
        return self.step is None or (item - self.start) % self.step == 0

    def __repr__(self):
        return f'All[{self.start}:{self.end}:{self.step}]'


class SubFilter(Container):
    def __init__(self, base, sub):
        if not isinstance(sub, Container):
            sub = (sub,)
        self.sub = sub
        self.base = base

    def __contains__(self, item):
        return (item in self.base) and (item not in self.sub)

    def __repr__(self):
        return f'{self.base!r} - {self.sub!r}'


class AddFilter(Filter):
    def __init__(self, *parts):
        self.parts = []
        for p in parts:
            if not isinstance(p, Container):
                p = (p,)
            self.parts.append(p)

    def __contains__(self, item):
        return any((item in p) for p in self.parts)

    def __repr__(self):
        return ' | '.join(repr(p) for p in self.parts)

    def __or__(self, other):
        if isinstance(other, type(self)):
            return type(self)(*self.parts, *other.parts)
        return type(self)(*self.parts, other)

    def __ror__(self, other):
        return self | other


class MulFilter(Filter):
    def __init__(self, *parts):
        self.parts = []
        for p in parts:
            if not isinstance(p, Container):
                p = (p,)
            self.parts.append(p)

    def __contains__(self, item):
        return all((item in p) for p in self.parts)

    def __repr__(self):
        return ' & '.join(repr(p) for p in self.parts)

    def __and__(self, other):
        if isinstance(other, type(self)):
            return type(self)(*self.parts, *other.parts)
        return type(self)(*self.parts, other)

    def __rand__(self, other):
        return self & other
