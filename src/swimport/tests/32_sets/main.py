from swimport.all import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))

swim(pools.primitive())
swim(pools.std_string())
swim(pools.c_string())

assert swim(pools.set('int'))
assert swim(pools.set('wchar_t const *'))
assert swim(pools.list('std::unordered_set<int>'))
assert swim(pools.set('char *'))
assert swim(pools.set('float'))
assert swim(pools.list('std::unordered_set<float>'))
assert swim(pools.set('std::string'))

assert swim(
    Function.Behaviour()(src)
)

swim.write('example.i')
print('ok!')
