import example

from swimport.tests.resources import *

p0 = example.point_create(1, 5)
assert_true(p0)
assert_eq(example.point_x(p0), 1)
p1 = example.point_create(5, 1)
f, n = example.point_middle(p0, p1)
assert_true(f)
assert_eq(example.point_x(n), 3)
