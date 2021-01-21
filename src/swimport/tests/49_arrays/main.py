from swimport.all import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))
swim(pools.primitive)
swim(pools.tuple(int, int))
swim(pools.array(int, 10))
swim(pools.array(int, 3))
swim(pools.array('std::pair<int, int>', 3))

assert swim(
    Function.Behaviour()(src)
)

swim.write('example.i')
print('ok!')
