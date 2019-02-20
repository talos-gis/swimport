from swimport import *


src = FileSource('src.h')
swim = Swim('example')

swim(pools.include(src))
swim(pools.c_string())

default_behaviour = Function.Behaviour()
free_ret_rule = '^big_.*' >> default_behaviour.replace(free_ret=True)

assert 'big_string' in swim(free_ret_rule(src))
assert swim(default_behaviour(src))

swim.write('example.i')
print('ok!')