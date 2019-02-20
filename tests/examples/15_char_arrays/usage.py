import example
import numpy as np
from tests.examples.resources import *

up = example.chars_upper("hello there")
up_ = np.array(list('HELLO THERE'), dtype='S1')
assert_true(np.array_equal(up, up_))

bad_arg = np.array(list("hi"))
assert_eq(np.dtype('U1'), bad_arg.dtype)
assert_ne(bad_arg.dtype, np.dtype('S1')) # bad_arg is of type U1, not S1 like we need
with AssertError(TypeError):
    example.chars_anylower(bad_arg)

assert_true(example.chars_anylower(np.array(list("Hi"), dtype='S1')))
assert_false(example.chars_anylower(np.array(list("HI THERE"), dtype='S1')))