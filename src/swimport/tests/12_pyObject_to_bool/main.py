from swimport.all import *


src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))
swim(pools.primitive(blacklist='bool'))
swim(pools.c_string)
swim(pools.bool())

assert swim(Function.Behaviour()(src)) > 0

swim.write('example.i')
print('ok!')