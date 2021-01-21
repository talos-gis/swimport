import example
from swimport.tests.resources import assert_eq, assert_true

assert_eq(example.fibonacci(5), 5)

d, r = example.divmod(90, 8)
assert_eq(d, 11)
assert_eq(r, 2)

# a demonstration of SWIG's None ignoring quirk
i, j = example.choose(False)
assert_true(i)
assert_eq(j, 5)

assert_eq(example.choose(True), 5)
