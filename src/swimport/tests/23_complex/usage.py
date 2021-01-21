import example

from swimport.tests.resources import *

assert_isclose(example.radius(1 + 1j), 2 ** 0.5)
assert_eq(example.radius(1), 1)
assert_eq(example.radius(1.7), 1.7)

assert_isclose(example.root(2), -1)
assert_isclose(example.root(4), 1j)

b, c = example.complements(2 + 3j)
assert_isclose(b, 2)
assert_isclose(c, 3j)
