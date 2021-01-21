import example

from swimport.tests.resources import *

point = example.Point_Create()
assert_eq(point[0], 0)
assert_eq(point[1], 0)

assert_eq(example.Point_Radius((3, 4)), 5)

px, py = example.Point_Components((3, 4))

assert_eq(px, (3, 0))
assert_eq(py, (0, 4))

l0 = [0, 9, 4.1, 6]
l1 = example.inc(l0)
assert_is(l0, l1)
assert_eq(l1, [1, 10, 5.1, 7])
