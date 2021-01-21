from swimport.all import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))

assert 'taste' in swim(
    ('taste' >> VariableGetSetBehaviour())(src)
)

assert 'scent' in swim(
    ('scent' >> VariableGetSetBehaviour(set_=False))(src)
)

assert 'error_occurred' in swim(
    ('error_occurred' >> Variable.Behaviour(immutable=True))(src)
)

assert 'error_occurred' not in swim(
    Variable.Behaviour()(src)
)

assert swim(Function.Behaviour()(src))

swim.write('example.i')
print('ok!')
