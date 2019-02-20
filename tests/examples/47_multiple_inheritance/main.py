from swimport import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))
swim(pools.primitive)

cswim = ContainerSwim('Foo', src)
assert cswim(... >> FunctionBehaviour())
assert swim(cswim)

cswim = ContainerSwim('Bar', src)
assert cswim(... >> FunctionBehaviour())
assert swim(cswim)

cswim = ContainerSwim('Baz', src)
assert cswim(... >> FunctionBehaviour())
assert swim(cswim)

swim.write('example.i')
print('ok!')
