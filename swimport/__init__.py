from swimport.__data__ import __version__, __author__
from swimport.model import \
    TriggerBehaviourSwimRule, FileSource, Trigger, Behaviour,\
    CPPObject, Function, Container, Variable, Enumeration, Typedef
from swimport.pools import pools
from swimport.swim import Swim
from swimport.typeswim import TypeSwimporting, FunctionBody, BuiltinTypemap

from swimport.functionswim import FunctionNameTrigger, FunctionBehaviour, ParameterNameTrigger, ParameterTypeTrigger,\
    ParameterBehaviour, ParameterRule
from swimport.typedefswim import TypedefAggregate, TypedefBehaviour, TypedefDestinationTrigger, TypedefSourceTrigger
from swimport.containerswim import ContainerNameTrigger, ContainerKindTrigger, ContainerBehaviour, ContainerSwim
from swimport.enumerationswim import EnumerationTrigger, EnumerationBehaviour, EnumBehaviour
from swimport.variableswim import VariableBehaviour, VariableNameTrigger, VariableTypeTrigger, VariableGetSetBehaviour

# todo static arrays?

# todo enum classes? we already do this, we just need see if its supported
# todo handle "using" statements (like typedefs): cppheaderparser doesn't support this
# todo multiset to counter?

# todo #define constants?
