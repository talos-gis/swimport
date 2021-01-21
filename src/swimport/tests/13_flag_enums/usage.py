import example
from swimport.tests.resources import *

assert_eq(example.Color.WHITE, 7)
assert_not_hasattr(example, 'WHITE')
assert_eq(example.Color.GREEN, example.Color.BLUE | example.Color.YELLOW)
assert_isinstance(example.Color.BLUE | example.Color.YELLOW, type(example.Color.GREEN))
assert_is(type(example.Color.GREEN), example.Color)

assert_true(example.is_primary(example.Color.RED))
assert_true(example.is_composite(example.Color.ORANGE))
assert_true(example.contains(example.Color.ORANGE, example.Color.YELLOW))
assert_eq(example.complement(example.Color.RED), example.Color.GREEN)
assert_isinstance(example.complement(example.Color.RED), type(example.Color.GREEN))
w, o0, o1 = example.triad(example.Color.GREEN)
assert_true(w)
assert_eq(o0, example.Color.BLUE)
assert_eq(o1, example.Color.YELLOW)
w, o0, o1 = example.triad(example.Color.BLACK)
assert_false(w)
assert_eq(o0, o1, example.Color.BLACK)
assert_eq(example.invert_color(example.Color.RED), example.Color.GREEN)