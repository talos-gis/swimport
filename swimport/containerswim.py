from typing import Container as Includer

from functools import partial

from swimport.__util__ import *
from swimport.model import Container, NameTrigger, SwimRule, object_swimporting, Source, SwimportingsResult, \
    RawSource, Function
from swimport.swim import Swim
from swimport.typeswim import TypeSwimporting, BuiltinTypemap, FunctionBody


class ContainerNameTrigger(Container.Trigger, NameTrigger):
    """A trigger for container names"""


class ContainerKindTrigger(Container.Trigger):
    """A trigger that filters containers by kind"""
    all_kinds = frozenset((Container.Kind.Union,
                           Container.Kind.Class,
                           Container.Kind.Struct))

    def __init__(self, valid_kind: Includer[Container.Kind]):
        """
        :param valid_kind: valid kinds of containers to accept
        """
        self.valid_kinds = valid_kind

    def is_valid(self, rule: SwimRule, obj: Container) -> bool:
        return super().is_valid(rule, obj) \
               and obj.kind in self.valid_kinds


@Container.set_default_trigger
def _(arg):
    """
    default trigger, trigger depends on arg's type:
    str: name trigger
    Container.Kind: only accept containers of that kind
    Collection: only accept containers of kinds inside the collection
    """
    if isinstance(arg, str):
        return ContainerNameTrigger(arg)
    if isinstance(arg, Container.Kind):
        return ContainerKindTrigger((arg,))
    if isinstance(arg, Includer):
        return ContainerKindTrigger(arg)
    raise TypeError('cannot parse argument as container trigger')


def container_type_import(name, args):
    p_port = partial(TypeSwimporting, name + '*',
                     to_py=BuiltinTypemap(name + '*'),
                     to_cpp=BuiltinTypemap(name + '*'),
                     to_cpp_check=BuiltinTypemap(name + '*'),
                     to_cpp_check_precedence=...)(**args)
    yield p_port
    p_to_py_func = p_port.to_py_func
    if p_to_py_func:
        to_py = FunctionBody.combine(p_to_py_func)(f"""     
                                                    return {p_to_py_func.function_name}(({name}*)(&input), ok, PACKED_UD(0));
                                                    """)
    else:
        to_py = None
    p_to_cpp_func = p_port.to_cpp_func
    if p_to_cpp_func:
        to_cpp = FunctionBody.combine(p_to_cpp_func)(f"""
                                                    auto ptr = {p_to_cpp_func.function_name}(input, ok, PACKED_UD(0));
                                                    if (!ok || PyErr_Occurred() != nullptr)
                                                        SWIM_RAISE_UNSPECIFIED;
                                                    return *ptr;
                                                    """)
    else:
        to_cpp = None
    p_to_cpp_check_func = p_port.to_cpp_check_func
    if p_to_cpp_check_func:
        to_cpp_check = FunctionBody.combine(p_to_cpp_check_func)(f"""
                                                                    return {p_to_cpp_check_func.function_name}(input, PACKED_UD(0));
                                                                    """)
    else:
        to_cpp_check = None

    port = partial(TypeSwimporting, name,
                   to_py=to_py,
                   to_cpp=to_cpp,
                   to_cpp_check=to_cpp_check,
                   to_cpp_check_precedence=...)(**args)
    yield port


@Container.set_default_behaviour
class ContainerBehaviour(Container.Behaviour):
    def __init__(self, out=True, inline=False, **type_args):
        """
        :param out: whether to prepare output typemaps for the type
        :param inline: whether to scope the container body in an inline scope instead of raw scope
        :param iter_maps: whether to apply iterator typemaps
        """
        self.out = out
        self.inline = inline
        self.type_args = type_args

    @object_swimporting
    def wrap(self, rule: SwimRule, obj: Container, swim):
        body_scope = Swim.add_inline if self.inline else Swim.add_raw

        swim.add_comment(obj)
        body = [obj.kind.value + ' ' + obj.name + '{', '\tpublic:']
        for m in obj.members:
            if m.access != 'public':
                raise ValueError('Default Container.Behaviour can only handle simple aggregate containers.'
                                 'Use the ContainerSwim object')
            body.append('\t\t' + m.body + ';')
        body.append('};')
        body_scope(swim, body)
        swim(container_type_import(obj.name, self.type_args))


class ContainerSwim:
    """A swimporting aggregate handling the scope of a single container."""

    # todo ability to mark methods as @abstractmethods

    def __init__(self, trigger, source: Source, *, director=False, wrapper_superclass=None, **type_args):
        """
        :param trigger: the trigger (or default trigger argument) with which to identify the proper container to import
        :param source: the source object to get the container from
        :param director: whether to insert a director for this class, allowing it to be subclassed from python
        :param type_args: additional arguments to the internal typeswimporting
        """
        self.director = director
        if self.director:
            type_args.setdefault('to_py', None)

        self.type_args = type_args
        self.wrapper_superclass = wrapper_superclass

        trigger = Container.Trigger(trigger)
        qualified = None
        for c in source:
            if trigger.is_valid(None, c):
                if qualified is None:
                    qualified = c
                else:
                    raise Exception(f'multiple containers matched: {c}, {qualified}, ...')
        if not qualified:
            raise Exception('no container matched')
        self.container: Container = qualified

        bases = list(self.container.public_bases)
        if bases:
            bases_str = ': public ' + ', public '.join(bases)
        else:
            bases_str = ''

        self._in_body = [
            Swim.add_raw(f'{self.container.kind.value} {self.container.name}{bases_str} {{')
        ]
        for m in self.container.members:
            if m.is_static:
                continue
            self._in_body.append(Swim.add_raw(f'{m.access}: {m.body}'))
        self._in_body.append(Swim.add_raw('public:'))

        self.extend = []

        self.post_body = []

    def __call__(self, rule: SwimRule) -> SwimportingsResult:
        """Process a rule over all the public members and functions of the container"""
        ret = SwimportingsResult()
        for o in self._importable_cpp_objects():
            if o.access != 'public':
                continue
            porting = rule.do(o)
            if porting is not None:
                self._in_body.append(porting)
                obj = getattr(porting, 'object', None)
                if obj:
                    ret += obj.name
                else:
                    ret += 1
        return ret

    def __iter__(self):
        yield from container_type_import(self.container.name, self.type_args)
        if self.director:
            yield Swim.add_raw(f'%feature("director") {self.container.name};')
        if self.wrapper_superclass:
            yield Swim.add_raw(f'%feature("python:abc",{self.wrapper_superclass}) {self.container.name};')
        yield from self._in_body
        if self.extend:
            yield Swim.add_raw('%extend {')
            yield from self.extend
            yield Swim.add_raw('}')
        yield Swim.add_raw('};')
        yield from self.post_body

    def _importable_cpp_objects(self):
        yield from (x for x in self.container.members if x.is_static)
        yield from self.container.methods

    def extend_method(self, sign, body, behaviour=...):
        """
        Add an extension method to the container
        :param sign: the signature of the method.
        :param body: the (cpp) body of the method. use $self instead of this.
        :param behaviour: the behaviour with which to import the method
        """
        if behaviour is ...:
            behaviour = Function.Behaviour()

        behaviour = behaviour.replace(body=body, body_scope=Swim.add_raw)

        i = iter(RawSource(sign))
        function = next(i, None)
        if next(i, None):
            raise Exception('multiple signatures detected')
        if not function:
            raise Exception('no signature')

        self.extend.append(behaviour.do(function))

    def extend_py_def(self, symbol, params, body, wrapper: str = ...):
        """
        Extend the container with a python method.
        :param symbol: the name of the function to add/replace
        :param params: the parameters of the function
        :param body: the (python) body of the function
        :param wrapper: if present, will wrap the new function (e.g. "staticmethod", "property").
            Default will copy the type of the previous value, if any.
        """
        py_code = ['__temp_store = getattr(' + self.container.name + ',"""' + symbol + '""",None)',
                   f'def __temp_def({params}):']
        py_code.extend(scope_lines(body, '', '', inline=False))
        if wrapper is ...:
            py_code.extend(['if isinstance(__temp_store, (classmethod, staticmethod, property)):',
                            '\t__temp_def = type(__temp_store)(__temp_def)'])
        elif wrapper:
            py_code.append(f'__temp_def = {wrapper}(__temp_def)')
        py_code.extend(['__temp_def.prev = __temp_store', self.container.name + '.' + symbol + ' = __temp_def',
                        'del __temp_store, __temp_def'])
        self.post_body.append(Swim.add_python(py_code))
