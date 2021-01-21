import operator as op
from cmath import isclose
from functools import partial

def ordered(op, n_mes):
    def ret(*args, **kwargs):
        if not args:
            return True
        if len(args) == 1:
            raise Exception('only one argument for assert')
        prev = args[0]
        for i in args[1:]:
            if not op(prev, i, **kwargs):
                raise AssertionError(f'{prev} {n_mes} {i}')
            prev = i

    return ret


assert_gt = ordered(op.gt, "<=")
assert_ge = ordered(op.ge, "<")
assert_lt = ordered(op.lt, ">=")
assert_le = ordered(op.le, ">")
assert_eq = ordered(op.eq, '!=')
assert_ne = ordered(op.ne, '==')
assert_is = ordered(op.is_, 'is not')
assert_is_not = ordered(op.is_not, 'is')
assert_in = ordered(lambda x, y: x in y, 'not in')
assert_not_in = ordered(lambda x, y: x not in y, 'in')


def asserts(op, n_mes):
    def ret(*args, **kwargs):
        if not op(*args, **kwargs):
            a = ', '.join(repr(a) for a in args) + ', '.join(f'{k!r}={v!r}' for k, v in kwargs.items())
            raise AssertionError(f'{n_mes}({a})')

    return ret


assert_isinstance = asserts(isinstance, 'not isinstance')
assert_not_isinstance = asserts(lambda x, y: not isinstance(x, y), 'isinstance')

assert_issubclass = asserts(issubclass, 'not issubclass')
assert_not_issubclass = asserts(lambda x, y: not issubclass(x, y), 'issubclass')

assert_true = asserts(bool, 'not ')
assert_false = asserts(op.not_, 'bool')

assert_not_hasattr = asserts(lambda a, b: not hasattr(a, b), 'hasattr')
assert_isclose = ordered(partial(isclose, abs_tol=1e-9), '!~=')