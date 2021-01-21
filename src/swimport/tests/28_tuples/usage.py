import example

from swimport.tests.resources import *

assert_eq(example.repeat(('a', 10)), 'aaaaaaaaaa')
assert_eq(example.first_lowercase('AAbcaF'), ('b', 2))

x = example.personnel()
jim, dwight, scott = x
assert_eq(jim[0].id, 0)
assert_eq(jim[0].age, 18)
assert_eq(jim[1:], ('jim', (1, 2)))
assert_eq(dwight[0].id, 1)
assert_eq(dwight[0].age, 27)
assert_eq(dwight[1:], ('dwight', (7, 11)))

assert_eq(scott[0].id, 2)
assert_eq(scott[0].age, 30)
assert_eq(scott[1:], ('mike', (55, 100)))
p_mike = example.person()
p_mike.age = -55
p_mike.id = 11

assert_true(example.is_ok((p_mike, "prison mike", (-89, 11))))
assert_false(example.is_ok((p_mike, "not prison mike", (-89, 11))))

assert_eq(example.factors(12), (2, 6))
assert_eq(example.factors(1337), (7, 191))

assert_true(example.is_ok([p_mike, "prison mike", (-89, 11)]))

assert_eq(example.empty(), ())
assert_eq(example.wrap(), ((),))
