from swimport.all import *

src = FileSource('src.h')
src_0 = FileSource('src_0.h')
src_1 = FileSource('src_1.h')
swim = Swim('example')
swim(pools.include(src))
swim(pools.primitive())

agg = TypedefAggregate()
assert 'nint' in agg(
    Typedef.Behaviour()(src_1, src, src_0)
)  # the TypedefAggregate makes sure to sort the typedefs regardless of the order the sources are in

assert 'nint' in swim(agg)  # forward all the imported aggregates to the main swim

assert swim(Function.Behaviour()(src))

swim.write('example.i')
print('ok!')
