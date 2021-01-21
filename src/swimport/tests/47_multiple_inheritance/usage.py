import example
from swimport.tests.resources import *

with AssertError(AttributeError):
    example.Foo()

bar = example.Bar()
assert_isinstance(bar, example.Bar)
assert_eq(bar.bar0(), 1)
assert_eq(bar.bar1(), 2)

baz = example.Baz()
assert_isinstance(baz, example.Baz)
assert_isinstance(baz, example.Bar)
assert_isinstance(baz, example.Foo)
assert_eq(baz.foo0(), 3)
assert_eq(baz.foo1(), 0)
assert_eq(baz.bar0(), 4)
assert_eq(baz.bar1(), 2)
assert_eq(baz.baz0(), 5)
