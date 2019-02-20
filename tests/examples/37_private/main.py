from swimport import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))

cswim = ContainerSwim('Point', src)

assert swim(cswim)

assert swim(Function.Behaviour()(src))

swim.write('example.i')
print('ok!')
