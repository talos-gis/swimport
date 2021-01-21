from swimport.all import *

src = FileSource('src.h')  # create a source object for  the header file
swim = Swim('example')  # create the main swim object
swim(pools.include(src))  # call the include pool for the source, and put that into the swim
default_behaviour = Function.Behaviour()  # create a method behaviour
method_rule_default = TriggerBehaviourSwimRule(..., default_behaviour, 'default')  # create a method rule

# equivelant:
# method_rule_default = ... >> default_behaviour
# alternatively:
# method_rule_default = default_behaviour

assert swim(
    method_rule_default(src)) > 0  # apply the rule to the source file, and check that at least one method was imported

swim.write('example.i')
print('ok!')
