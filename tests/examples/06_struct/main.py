from swimport import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))

assert 'Point' in swim(
    Container.Behaviour()(src)
)

assert swim(Function.Behaviour()(src))

swim.write('example.i')
print('ok!')
