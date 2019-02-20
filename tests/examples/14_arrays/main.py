from swimport import *


src = FileSource('src.h')
swim = Swim('example')

swim(pools.numpy_arrays(r"../resources"))
swim(pools.include(src))

assert swim(Function.Behaviour()(src)) > 0

swim.write('example.i')
print('ok!')