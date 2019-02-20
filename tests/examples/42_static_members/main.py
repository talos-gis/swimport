from swimport import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))
swim(pools.include('../resources/cpp_iterable.h'))
swim(pools.primitive)

cswim = ContainerSwim('Universe', src)

cswim(... >> Function.Behaviour())
cswim('next_id|meaning' >> Variable.Behaviour())
cswim('dimensions' >> VariableGetSetBehaviour())

assert swim(cswim)

swim.write('example.i')
print('ok!')
