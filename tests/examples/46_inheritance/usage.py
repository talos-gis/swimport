import math

import example
from tests.examples.resources import *

with AssertError(AttributeError):
    shape = example.Shape()

circle = example.Circle(0, 20, 5)
assert_isinstance(circle, example.Shape)
assert_isinstance(circle, example.Circle)

assert_eq(circle.x_min(), -5)
assert_eq(circle.x_max(), 5)
assert_true(circle.Contains(3, 23))
assert_true(circle.Contains(3, 17.9))
assert_isclose(circle.area(), 5 * 5 * math.pi, rel_tol=1e-1)

rect = example.Rectangle(10, 50, 6, 20)
assert_true(rect.Contains(11, 56))
assert_isinstance(rect, example.Shape)
assert_isinstance(rect, example.Rectangle)
assert_eq(rect.area(), 120)