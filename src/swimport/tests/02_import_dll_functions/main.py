from swimport.all import *

src = FileSource('addlib.h')
swim = Swim('example')
# swim(pools.include(src))  # don't include the header file, as we will define handles for all the functions in it
swim(pools.dlls('addlib'))  # add the necessary declarations for dll imports and specifically addlib.dll

# set a dll_detect, triggering swimport to recognize a function that should be loaded at runtime from a dll
default_behaviour = Function.Behaviour(dll_detect={'ADDLIB_API': 'addlib'})

assert swim(default_behaviour(src)) == 1

swim.write('example.i')
print('ok!')
