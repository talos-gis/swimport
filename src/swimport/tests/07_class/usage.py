import example
from swimport.tests.resources import *

point = example.Point_Create(3, 4)
assert_eq(point.x, 3)
assert_eq(point.y, 4)

assert_eq(example.Point_Radius(point), 5)

assert_eq(example.Point_Hamilton(point), 7)

px, py = example.Point_Components(point)

assert_eq(px.x, 3)
assert_eq(px.y, 0)
assert_eq(py.x, 0)
assert_eq(py.y, 4)

pi = example.Point_Inc(point)

assert_eq(pi.x, 4)
assert_eq(pi.y, 5)
