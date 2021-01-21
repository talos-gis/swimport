import example
from swimport.tests.resources import *

point = example.Point(3, 4)
assert_eq(point.x, 3)
assert_eq(point.y, 4)
assert_isinstance(point, example.Point)
assert_not_hasattr(point, 'z')

p2 = example.decompose(point)
assert_eq(p2.x, 3)
assert_eq(p2.y, 0)
assert_isinstance(p2, example.Point)

point.set_z('a')
assert_eq(point.get_z(), 'A')

p, r = p2.polar()
assert_eq(p, 0)
assert_eq(r, 3)

p, r = point.polar()
assert_eq(r, 5)

q1, q3, q4 = point.mirrors()
assert_eq(q1.x, -3)
assert_eq(q3.x, -3)
assert_eq(q4.x, 3)

assert_eq(q1.y, 4)
assert_eq(q3.y, -4)
assert_eq(q4.y, -4)