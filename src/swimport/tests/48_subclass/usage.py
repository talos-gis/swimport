import example
from swimport.tests.resources import *

with AssertError(Exception):
    shape = example.Foo()


class Odd(example.Foo):
    def foo(self, i):
        return i % 2 == 1

    def baz(self, it):
        return sum(it) < 10

    def beer(self):
        return [1, 1, 2, 3, 5]


odd = Odd()
assert_isinstance(odd, example.Foo)
assert_true(odd.foo(5))
assert_true(odd.foo(1))
assert_eq(odd.bar(), 5)
assert_eq(odd.booz(), 5)
assert_eq(odd.boun(), 12)
