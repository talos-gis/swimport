import example
from tests.examples.resources import *

p = example.Polynomial.from_coefficients([-2, 0, 1])
assert_eq(p(10), 98)

p = example.Polynomial.from_roots([2, 3])
p2 = example.Polynomial.from_roots(2, 3)
assert_eq(p(10), p2(10), 8 * 7)

c, l, s = example.Polynomial.pows(3)

assert_eq(c(52), 1)
assert_eq(l(52), 52)
assert_eq(s(52), 52 ** 2)

p = example.Polynomial.from_points([
    (1, 1),
    (2, 1),
    (0, 8)
])
assert_eq(p(1), p(2), 1)
assert_eq(p(0),8)
