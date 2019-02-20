from swimport import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))
swim(pools.include('../resources/pycall_surrogate.h'))

swim(pools.primitive)
swim(pools.std_string)

swim(pools.callable('void'))
swim(pools.callable('double', 'double'))
swim(pools.callable('bool', 'int', 'std::string'))

assert swim(
    Function.Behaviour(exception_check=...)(src)
)

swim.write('example.i')
print('ok!')
