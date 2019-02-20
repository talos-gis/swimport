from swimport import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))
swim(pools.include('../resources/cpp_iterable.h'))
swim(pools.primitive)
swim(pools.std_string)

cswim = ContainerSwim('Polynomial', src)

cswim(... >> FunctionBehaviour())

assert swim(cswim)

assert swim(Variable.Behaviour()(src))

swim.write('example.i')
print('ok!')
