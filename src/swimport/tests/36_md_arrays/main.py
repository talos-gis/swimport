from swimport.all import *

src = FileSource('src.h')
swim = Swim('example')

swim(pools.numpy_arrays(r"../resources", max_dim=3))
swim(pools.include(src))

assert swim(Function.Behaviour()(src)) > 0

swim.write('example.i')
print('ok!')
