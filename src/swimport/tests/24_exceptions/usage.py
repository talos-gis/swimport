import example

from swimport.tests.resources import *

assert_eq(example.factorial(5), 120)
with AssertError(ValueError, "negative value"):
    example.factorial(-1)
with AssertError(OSError):
    example.open()

with AssertError(ValueError, 'division by zero'):
    example.inv(0)
with AssertError(FileNotFoundError):
    example.inv(-1)
with AssertError(Exception, '-2'):
    example.inv(-2)
with AssertError(Exception, 'an non-exception was thrown'):
    example.inv(-3)
with AssertError(NameError, 'waldo'):
    example.inv(-4)
with AssertError(KeyError):
    example.inv(-5)
assert_eq(example.inv(5), 0.2)

with AssertError(FileNotFoundError):
    example.copen()
