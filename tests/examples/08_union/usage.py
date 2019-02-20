import example
from tests.examples.resources import *

p1 = example.Padded_Create(257)
assert_eq(p1.w, 257)
assert_eq(p1.n, '\x01')

p2 = example.Padded_Create(chr(25))
assert_eq(p2.w, 25, ord(p2.n))

f, p1_ = example.Padded_Trim(p1)
assert_false(f)
assert_eq(p1_.w, 1, ord(p1_.n))

t, p2_ = example.Padded_Trim(p2)
assert_true(t)
assert_eq(p2_.w, 25, ord(p2_.n))

p3 = example.Padded_Create(257)
p3_ = example.Padded_Trim_Inplace(p3)
assert_eq(ord(p3_.n), 1, p3.w)
