import example
from swimport.tests.resources import *

b1 = example.mk(6)
assert_eq(example.extract(b1), 6)

b2 = example.mk(89)
assert_eq(example.extract(b2), 89)

b3 = example.sum(b2, b1)
assert_eq(example.extract(b3), 95)

b4, b5 = example.div(b2, b1)
assert_eq(example.extract(b4), 14)
assert_eq(example.extract(b5), 5)
