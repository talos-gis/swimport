from swimport import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))
swim(pools.complex())

assert swim(Function.Behaviour()(src))

swim.write('example.i')
print('ok!')
