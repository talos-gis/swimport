import example

from tests.examples.resources import *

p = example.primes()
assert_isinstance(p, list)
assert_eq(p, [2, 3, 5, 7, 11, 13, 17, 19, 23, 29])

z = example.zip([1, 2, 3], range(5, 8))
assert_isinstance(z, list)
assert_eq(z, [(1, 5), (2, 6), (3, 7)])

with AssertError(TypeError):
    example.zip([1, 2, 3], range(5, 9))

with AssertError(TypeError):
    example.zip([1, 2], range(5, 8))