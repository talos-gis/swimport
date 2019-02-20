import math

from tests.examples.resources import *

import example

assert_eq(example.norm((2, 3, 6)), 7)
assert_eq(example.norm((4, 3)), 5)


def near(a, b):
    return len(a) == len(b) \
           and all(abs(i - j) <= 0.0001 for (i, j) in zip(a, b))


assert_true(near(example.fromPolar(math.pi / 6), (0.86602, 0.5, 0)))
assert_true(near(example.fromPolar(math.pi / 4, math.sqrt(2)), (1, 1, 0)))
assert_true(near(example.fromPolar(0, 10, 5), (10, 0, 5)))

assert_true(near(example.middle((0, 1, 2), (5, 3)), (2.5, 2, 1)))
x, y, z = example.components((5, 6, 7))
assert_true(near(x, (5, 0, 0)))
assert_true(near(y, (0, 6, 0)))
assert_true(near(z, (0, 0, 7)))
s, p = example.mk_point(5, 6, 8)
assert_true(near(p, (5, 6, 8)))
assert_true(s)
s, p = example.mk_point(5, 6, -1)
assert_true(near(p, (5, 6, -1)))
assert_false(s)

q = example.flip_xy(p)
assert_true(near(q, (6, 5, -1)))
assert_true(near(p, (5, 6, -1)))
