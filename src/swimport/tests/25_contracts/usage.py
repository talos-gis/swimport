import example

from swimport.tests.resources import *

assert_eq(example.factorial(5), 120)
with AssertError(RuntimeError):
    example.factorial(-1)

assert_eq(example.inv(5), 0.2)
with AssertError(RuntimeError):
    example.inv(0)

assert_eq(example.sign(0), 0)
assert_eq(example.sign(12), 1)
assert_eq(example.sign(-9), -1)

with AssertError(RuntimeError):
    example.sign(5)