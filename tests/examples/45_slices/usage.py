import example

from tests.examples.resources import *

assert_true(example.in_slice(slice(1, 10, 2), 5))
assert_false(example.in_slice(slice(1, 10), 12))
assert_true(example.in_slice(slice(1, None, -1), -12))

assert_true(example.in_continuum(slice(1.2, 3.8), 2.3))
j = example.join_continuum(slice(1, 5.5), slice(4, 8.8))
assert_eq(j, slice(1, 8.8))

with AssertError(ValueError):
    example.in_continuum(slice(1.2, 3.8, 1), 2.3)
