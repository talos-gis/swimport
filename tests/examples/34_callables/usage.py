import example

from math import sqrt

from tests.examples.resources import *


def knock(a=1):
    global x
    x += a

x = 0
example.knock(knock)
assert_eq(x, 1)
assert_isclose(example.search(lambda x: x ** 2 - 2, 0, 2), sqrt(2))


def roman_callback(lim):
    d = {}

    def callback(num, roman):
        d[num] = roman
        return num < lim

    callback.d = d

    return callback


rc = roman_callback(5)
example.report_romans(rc)

assert_eq(rc.d, {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V'})

with AssertError(TypeError):
    example.knock(5)

with AssertError(TypeError):
    example.search(lambda: -2, 0, 2)
