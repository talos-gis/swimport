import example
from tests.examples.resources import *

assert_eq(example.SWEET, 0)
assert_eq(example.SOUR, 1)
assert_eq(example.SALTY, 6)
assert_eq(example.BITTER, 5)
assert_eq(example.UMAMI, -1)

assert_true(example.good_flavor(example.SWEET))
assert_false(example.good_flavor(example.BITTER))

assert_true(example.is_made_up(example.UMAMI))

assert_eq(example.opposite(example.SWEET), example.BITTER)

f, u = example.get_made_up()

assert_eq(f, 5)
assert_eq(u, example.UMAMI)

assert_eq(example.invert(example.SWEET), example.BITTER)

assert_eq(example.Color.WHITE, 7)
assert_not_hasattr(example, 'WHITE')
assert_eq(example.Color.GREEN, example.Color.BLUE | example.Color.YELLOW)
# NOTE: we are demonstrating here value equivalence, note that type(example.Color.BLUE | example.Color.YELLOW) is int!
# this is because example.Color is an enum.IntEnum, not an enum.Flag. Flags will be properly tackled in a example 13
assert_not_isinstance(example.Color.BLUE | example.Color.YELLOW, type(example.Color.GREEN))
assert_isinstance(example.Color.BLUE | example.Color.YELLOW, int)

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