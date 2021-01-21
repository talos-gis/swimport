from swimport.all import *

src = FileSource('src.h')
swim = Swim('example')

swim(pools.include(src))
swim(pools.primitive)
swim(pools.slice('double', ...))
swim(pools.slice('int', ..., ...))

assert swim(Function.Behaviour()(src))

swim.write('example.i')
print('ok!')
