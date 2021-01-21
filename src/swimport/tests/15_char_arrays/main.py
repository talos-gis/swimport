from swimport.all import *


src = FileSource('src.h')
swim = Swim('example')

swim(pools.c_string)
swim(pools.numpy_arrays(r"../resources", allow_char_arrays=True))
swim(pools.include(src))

assert swim(Function.Behaviour()(src)) > 0

swim.write('example.i')
print('ok!')