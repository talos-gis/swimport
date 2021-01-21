import example

from swimport.tests.resources import *

assert_eq(example.mutate(10, True), 11)
assert_eq(example.mutate(10, False), 9)

assert_eq(example.mutate(10, "hello world"), 11)
assert_eq(example.mutate(10, ()), 9)

assert_eq(example.is_ok(None), 'ERROR')
assert_eq(example.is_ok({1, 2, 3}), 'OK')

s, o = example.sum_of_digits(1337, 10, False)
assert_eq(s, 14)
assert_is(o, True)

s, o = example.sum_of_digits(1337, 10, ())
assert_eq(s, 14)
assert_is(o, True)

s, o = example.sum_of_digits(17, 10, ())
assert_eq(s, 8)
assert_is(o, False)

s, o = example.sum_of_digits(1337, 10, ...)
assert_eq(s, 14)
assert_is(o, True)

assert_eq(example.sign([]), -1)
assert_eq(example.sign(-1.0), 1)  # sign(bool)
assert_true(example.sign(-1))  # trigger sign(int)

assert_true(example.is_even({}))
assert_false(example.is_even(range(12)))
assert_false(example.is_even(int))
assert_true(example.is_even(10))


class A:
    def __bool__(self):
        raise Exception('A error')


with AssertError(text='A error'):
    example.is_ok(A())

assert_eq(example.foo("hi"), 1)
assert_eq(example.foo(""), 1)
assert_eq(example.foo(2.0), 2)
assert_eq(example.foo(True), 2)
