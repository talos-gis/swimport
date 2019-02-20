import example

from tests.examples.resources import *

assert_true(example.any_upper("abCa"))
assert_false(example.any_upper("abca"))
assert_false(example.any_upper(''))

x = example.big_string(100)
assert_eq(x[0:10], '0123456789')
assert_eq(len(x), 100)
assert_lt(check_memory_deg(lambda: example.big_string(1_000_000), 100), 0.2)

y = example.small_string()
assert_eq(y, 'little old me')
assert_lt(check_memory_deg(example.small_string, 100), 0.1)

c = example.str_mul('abc', 10)
assert_eq(c, 'abc' * 10)
assert_lt(check_memory_deg(lambda: example.str_mul('abacus', 1_000), 100), 0.2)

h = example.hebrew()
assert_eq(h,
       "שלום")
assert_eq(len(example.str_mul(h, 10)), len(h) * 10)

assert_false(example.any_upper("0\0 A"))

assert_is(example.get_null(), None)
assert_lt(check_memory_deg(example.get_null, 100), 0.2)
