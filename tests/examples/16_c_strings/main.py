from swimport import *


src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))
swim(pools.c_string)

default_behaviour = Function.Behaviour()
free_ret_rule = '^big_.*' >> default_behaviour.replace(free_ret=True)

assert swim(free_ret_rule(src)) > 0
assert swim(default_behaviour(src)) > 0

swim.write('example.i')
print('ok!')