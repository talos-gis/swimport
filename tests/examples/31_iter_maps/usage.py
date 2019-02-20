import example

from tests.examples.resources import *

assert_not_isinstance(example.count_chars(""), dict)
assert_eq(dict(example.count_chars("abrakadabra")), {'a': 5, 'b': 2, 'r': 2, 'k': 1, 'd': 1})
assert_eq(list(example.count_chars("")), [])

assert_eq(example.from_factors({1: 2, 5: 3, 2: 4}), 125 * 16)
assert_eq(example.from_factors([(1, 2), (5, 3), (2, 4)]), 125 * 16)

assert_true(example.did_john_escape(''))
assert_true(example.did_john_escape({'jim': (5, 10)}))
assert_true(example.did_john_escape([('john', (100, -5))]))

assert_false(example.did_john_escape({'jim': (5, 12), 'john': (2, -8)}))

assert_eq(dict(example.components((10, 100))), {0: (10, 0), 1: (0, 100)})
