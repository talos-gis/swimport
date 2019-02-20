from swimport import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))
swim(pools.include('../resources/cpp_iterable.h'))
swim(pools.primitive)

cswim = ContainerSwim('Shape', src)
assert cswim(... >> FunctionBehaviour())
assert swim(cswim)

cswim = ContainerSwim('Circle', src)
assert cswim(... >> FunctionBehaviour())
assert swim(cswim)

cswim = ContainerSwim('Rectangle', src)
assert cswim(... >> FunctionBehaviour())
assert swim(cswim)

swim.write('example.i')
print('ok!')
