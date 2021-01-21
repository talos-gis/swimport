import example
from swimport.tests.resources import *

assert_eq(example.Universe.meaning, 42)
example.cvar.Universe_next_id = 3
assert_eq(example.cvar.Universe_next_id, 3)
u = example.Universe()
assert_eq(u.get_id(), 3)
assert_eq(example.cvar.Universe_next_id, u.next_id, 4)

assert_eq(example.Universe.get_dimensions(), 3)
example.Universe.set_dimensions(42)
assert_eq(example.Universe.get_dimensions(), 42)