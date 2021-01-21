from swimport.all import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))
swim(pools.include('../resources/cpp_iterable.h'))
swim(pools.primitive)

cswim = ContainerSwim('Point', src, arbitrary_initializer='{0,0}')

cswim(... >> FunctionBehaviour())

assert swim(cswim)

assert swim(Function.Behaviour()(src))

swim.write('example.i')
print('ok!')
