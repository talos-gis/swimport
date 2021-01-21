import example
import numpy as np

from swimport.tests.resources import *

assert_eq(example.sum(np.array((10, 100, 1))), 111)
assert_eq(example.sum([1, 2, 3]), 6)
assert_eq(example.sum(range(3)), 3)
assert_eq(example.sum((5.9, 1.9)), 6)  # known quirk

digits = example.digits(12345)
assert_isinstance(digits, np.ndarray)

assert_true(np.allclose(digits, [5, 4, 3, 2, 1]))

x = np.arange(5, dtype=float)
example.inc(x, 10)

assert_true(np.array_equal(x, [10, 11, 12, 13, 14]))

x = np.array([[1, 2], [3, 4]], dtype=float)  # rank 2 array
example.inc(x, 1)
assert_true(np.array_equal(x, [[2, 3], [4, 5]]))

assert_lt(check_memory_deg(example.very_big_array), 0.1)
assert_lt(check_memory_deg(example.very_big_array_malloc), 0.1)

x = example.very_big_array_view()
assert_true(np.array_equal(x, [0]*1000))
y = example.very_big_array_view()
x[0] = 1
assert_eq(y[0], 1)
del x
assert_eq(y[0], 1)