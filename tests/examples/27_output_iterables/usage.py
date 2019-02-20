import example

from tests.examples.resources import *

from itertools import islice

f = example.fib(10)
assert_not_isinstance(f, list)
i = iter(f)
assert_eq(list(i), [0, 1, 1, 2, 3, 5, 8, 13])
assert_eq(list(example.digits(123)), [3, 2, 1])
assert_eq(list(example.names()), ['jim', 'victor', 'loa'])
assert_eq(list(example.points()), [(1, 2), (2, 3), (3, 4)])
assert_eq(list(list(r) for r in example.matrix()), [[1, 2, 3], [2, 3, 4], [3, 4, 5]])
people = example.people()
assert_eq([x.id for x in people], [15, 47, 7])
assert_eq([x.age for x in people], [20, 98, 3])
del people


def half_use_list():
    l = list(islice(example.strings(), 2))
    return l


assert_lt(check_memory_deg(half_use_list), 0.2)
