from swimport import *


src = FileSource('src.h')
swim = Swim('example')

swim(pools.include(src))
swim(pools.buffer)

default_behaviour = Function.Behaviour()
assert swim(default_behaviour(src)) > 0

swim.write('example.i')
print('ok!')