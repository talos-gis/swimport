from swimport import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))

default_behaviour = Function.Behaviour()

# create a new behaviour that treats all pointers as inout parameters, and all other
inc_behaviour = default_behaviour.replace(
    parameter_rules=[ParameterTypeTrigger(r'.*\*') >> ParameterBehaviour.inout]
                    + default_behaviour.parameter_rules
)
inc_rule = 'inc' >> inc_behaviour
# equivalent
# inc_rule = Method.Trigger('inc') >> inc_behaviour
# alternatively
# inc_rule = MethodNameTrigger('inc') >> inc_behaviour

y = swim(inc_rule(src))
assert 'inc' in y == 1

# note: behaviours can be used as rules that accept all objects they encounter of the proper types
assert 'inc' not in swim(default_behaviour(src)) > 0  # get the rest of the methods

swim.write('example.i')
print('ok!')
