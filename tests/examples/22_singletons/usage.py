import example

from tests.examples.resources import *

assert_eq(example.fib(5, 0, 1), 5)
assert_eq(example.fib(10, ...), 55)
assert_eq(example.fib(5, 1), 5)

with AssertError((TypeError, NotImplementedError)):
    example.fib(10, None)

with AssertError(TypeError):
    example.accept_only_notimplemented(...)

assert_true(example.accept_only_notimplemented(NotImplemented))

assert_eq(example.count("abc\0oaia", 'a', 1, 6), 1)
assert_eq(example.count("abc\0oaia", 'a', 1, None), 0)
assert_eq(example.count("abc\0oaia", 'a', None, 6), 2)
assert_eq(example.count("abc\0oaia", 'a', None, None), 1)

assert_is(example.get_ellipsis(), ...)
assert_is(example.get_none(), None)
assert_is(example.get_ni(), NotImplemented)

for s in (None, NotImplemented, ...):
    c = example.code(s)
    efc = example.from_code(example.code(s))
    assert_is(efc, s)
