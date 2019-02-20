import example
from tests.examples.resources import *

point = example.Point_Create(3, 4)
assert_eq(point.x, 3)
assert_eq(point.y, 4)
assert_isinstance(point, example.Point)

point = example.Point()
point.x = 3
point.y = 4
assert_eq(point.x, 3)
assert_eq(point.y, 4)
assert_isinstance(point, example.Point)
assert_not_hasattr(point, 'z')

p2 = example.decompose(point)
assert_eq(p2.x, 3)
assert_eq(p2.y, 0)
assert_isinstance(p2, example.Point)
