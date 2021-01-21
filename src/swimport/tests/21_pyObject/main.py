from swimport.all import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))
swim(pools.pyObject)

assert swim(Function.Behaviour()(src))

swim.write('example.i')
print('ok!')
