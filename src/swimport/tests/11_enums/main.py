from swimport.all import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))

assert 'Flavor' in swim(
    ('Flavor' >> Enumeration.Behaviour())(src)
)

assert 'Color' in swim(
    ('Color' >> EnumBehaviour())(src)
)

assert swim(Function.Behaviour()(src))

swim.write('example.i')
print('ok!')
