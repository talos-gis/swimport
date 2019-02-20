import example
from tests.examples.resources import *

b1 = example.mul(1, 2)
assert_eq(b1, 2)

assert_eq(example.mul(6, 89), 22)

f, r = example.div(89, 6)
assert_eq(f, 14)
assert_eq(r, 5)

assert_eq(example.inc(254), 255)
assert_eq(example.dec(1), 0)

assert_eq(example.round(215), 214)
