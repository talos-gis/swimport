from swimport import *

src = FileSource('src.h')
swim = Swim('example', directors='1')
swim(pools.include(src))
swim(pools.include('../resources/cpp_iterable.h'))
swim(pools.primitive)
cswim = ContainerSwim('Foo', src, director=True)
assert cswim(... >> FunctionBehaviour(exception_check=...))
assert swim(cswim)

swim.write('example.i')
print('ok!')
