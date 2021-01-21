import example
from swimport.tests.resources import *

line = example.LineSegment()

line.start = (0, 0)
line.end = (3, 4)

assert_eq(line.start, (0, 0))
assert_eq(line.end, (3, 4))

assert_isclose(line.angle(), 0.927295218)
