import example

from swimport.tests.resources import *

assert_eq(example.sum([1, 2, 3, 4]), 10)
assert_eq(example.sum(x ** 2 for x in range(30) if '7' in str(x)), 7 ** 2 + 17 ** 2 + 27 ** 2)

x = (x ** 2 for x in range(3))
assert_eq(example.sum(x), 5)
assert_eq(example.sum(x), 0)
assert_eq(example.sum(iter((1, 3, 4))), 8)

assert_eq(example.max_len("hi there, my name is jim".split()), 6)
assert_eq(example.max_len("jim"), 1)

with AssertError(TypeError):
    example.sum(5)

with AssertError(TypeError):
    example.sum((5, "hi"))

with AssertError(TypeError):
    example.sum(("hi",))
assert_eq(example.agg([
    (0, 1),
    (2, 3),
    (5, 6),
]), (7, 10))

assert_eq(example.agg(
    (x, 2 * x) for x in range(6)
), (15, 30))
with AssertError(TypeError):
    example.agg(12)

with AssertError(TypeError):
    example.agg({
        7, (1, 2)
    })


def person(id, age):
    ret = example.person()
    ret.id = id
    ret.age = age
    return ret


assert_eq(example.oldest_person_id([
    person(1, 20),
    person(4, 75),
    person(10, 1)
]), 4)

with AssertError(TypeError):
    example.agg(-18)

with AssertError(TypeError):
    example.agg("howdy ho!")

assert_true(example.any_neg([1, 5, -8, 15, 3, 17]))
assert_false(example.any_neg(range(15)))

assert_lt(check_memory_deg(lambda: example.any_neg([1, 5, -8, 15, 3, 17])), 0.2)

assert_eq(example.sum_of_products([
    range(1, 4),  # 3! = 6
    [2, 2, 2],  # 8
    (i ** 2 for i in range(1, 20) if '7' in str(i))  # 7**2 * 17**2 = 14161
]), 6 + 8 + 14161)
