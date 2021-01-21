import math

from swimport.tests.resources import *

import example

assert_eq(example.zero, (0, 0))
assert_eq(example.cvar.origin, (0, 0))

example.cvar.origin = (4, 3)

assert_eq(example.mag_origin(), 25)

example.cvar.corners = [(4, 8), (6, 5), (7, 9), (12, 10)]
assert_eq(example.count_corners(), 4)

with AssertError(TypeError):
    example.cvar.corners = 15

with AssertError(Exception):
    # the exception is of an ambiguous type because we raised a system error in the to_py when defining the type
    example.cvar.corners = [15]

assert_eq(example.cvar.corners, [(4, 8), (6, 5), (7, 9), (12, 10)])
