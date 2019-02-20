from tests.examples.resources import *

import example

assert_eq(example.norm((2, 3, 6)), 7)
assert_eq(example.norm((4, 3)), 5)
assert_eq(example.norm(None), -1)

assert_eq(example.neg((1, 2, 3)), (1, 2, -3))
assert_eq(example.neg((1, 2)), (1, 2, 0))

with AssertError(SystemError):
    example.neg(None)
