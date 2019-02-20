from enum import IntFlag
from swimport import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))

assert 'Color' in swim(
    ('Color' >> EnumBehaviour(super_cls=IntFlag))(src)
)

assert swim(Function.Behaviour()(src))

swim.write('example.i')
print('ok!')
