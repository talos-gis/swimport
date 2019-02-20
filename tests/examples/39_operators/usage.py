import example
from tests.examples.resources import *

p = example.Polynomial(5)

assert_eq(p(-1), 5)
x = example.x
assert_eq(x(-2), -2)

sq = x*x

assert_eq(sq(12), 144)

root_2 = x * x - example.Polynomial(2)

assert_eq(root_2(2), 2)
assert_isclose(root_2(2 ** 0.5), 0)

with AssertError(TypeError):
    poly = x*3

assert_eq(str(root_2), "-2*x^0+1*x^2+")