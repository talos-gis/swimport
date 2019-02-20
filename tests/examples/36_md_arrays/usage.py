import example
import numpy as np

from tests.examples.resources import *

assert_eq(example.sum(np.array([[[1, 2], [2, 3]], [[3, 4], [4, 5]], [[1, 2], [2, 3]], [[3, 4], [4, 5]]])), 48)

assert_eq(example.product(np.array([[[1, 2], [2, 3]], [[3, 4], [4, 5]]])),
          example.product(np.array([1, 2, 2, 3, 3, 4, 4, 5])),
          2880)

a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6, 7], [8, 9, 10]])
c = example.mul(a, b)
assert_true(np.array_equal(c, a @ b))
