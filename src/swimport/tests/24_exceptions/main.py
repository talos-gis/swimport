from swimport.all import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))

method_rule_default = Function.Behaviour(exception_check=...)
assert swim(method_rule_default(src))

swim.write('example.i')
print('ok!')
