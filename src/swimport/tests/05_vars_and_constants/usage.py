import example
from swimport.tests.resources import *

assert_eq(example.pi, 3.14)
assert_eq(example.tau, 6.28)
assert_eq(example.one, 1)
assert_eq(example.factorial(5), 120)

assert_not_hasattr(example.cvar, 'pi')
assert_not_hasattr(example, 'mood')
assert_not_hasattr(example, 'error_occurred')

# all variables that are expected to change (i.e. not constants) must be accessed through cvar
assert_is(example.cvar.error_occurred, False)
assert_eq(example.factorial(-1), 0)
assert_is(example.cvar.error_occurred, True)
example.resetError()
assert_is(example.cvar.error_occurred, False)

example.cvar.mood = 5
assert_eq(example.getMood(), example.cvar.mood, 5)

with AssertError(AttributeError):
    # demonstrate that error_occurred is read-only from the python side
    example.cvar.error_occurred = True

assert_eq(example.get_taste(), 0)
example.set_taste(1)
assert_eq(example.get_taste(), 1)

assert_not_hasattr(example.cvar, 'taste')
assert_not_hasattr(example, 'taste')

assert_eq(example.get_scent(), 5)
example.inc_scent()
assert_eq(example.get_scent(), 6)

assert_not_hasattr(example.cvar, 'scent')
assert_not_hasattr(example, 'scent')
assert_not_hasattr(example, 'set_scent')
