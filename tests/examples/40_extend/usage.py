import example
from tests.examples.resources import *

p = example.Polynomial(5)

assert_eq(p(-1), 5)
x = example.x
assert_eq(x(-2), -2)

sq = x * x

assert_eq(sq(12), 144)

root_2 = x * x - example.Polynomial(2)

assert_eq(root_2(2), 2)
assert_isclose(root_2(2 ** 0.5), 0)

assert_eq(str(root_2), "-2*x^0+1*x^2+")

poly = 3 * x - 6

assert_eq(poly(9), 21)

poly = (x - 1) * (x + 6)

assert_eq(poly(1), poly(-6), 0)

poly = x ** 2 - x - 1

assert_isclose(poly(1.61803398875), poly(-0.61803398875), 0)

poly = x ** 3

assert_eq(poly(range(10)), [0, 1, 8, 27, 64, 125, 216, 343, 512, 729])
