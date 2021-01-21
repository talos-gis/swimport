from swimport.all import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))

# we need to disable the standard iterable types because they create maps for vectors that we intend to overwrite
swim(pools.primitive(additionals=False, out_iterable_types=(), in_iterable_types=()))
swim(pools.std_string(out_iterable_types=(), in_iterable_types=()))
swim(pools.c_string(out_iterable_types=(), in_iterable_types=()))

assert swim(
    ('person' >> Container.Behaviour(out_iterable_types=(), in_iterable_types=()))(src)
)

assert swim(
    TypeSwimporting('point',
                    to_py="""
                    return Py_BuildValue("ii",input.x, input.y);
                    """,
                    to_cpp="""
                    int x, y;
                    if (!PyArg_ParseTuple(input, "ii",&x, &y)) {ok=false; return {};}
                    return{x,y};
                    """,
                    out_iterable_types=(), in_iterable_types=())
)

assert swim(pools.list('int'))
assert swim(pools.list('wchar_t const *'))
assert swim(pools.list('point'))
assert swim(pools.list('person'))
assert swim(pools.iter('int', cpp_name='std::deque<?>', output=tuple))
assert swim(pools.list('std::deque<int>'))
assert swim(pools.list('char *'))
assert swim(pools.iter('float', cpp_name='std::deque<?>', output=tuple))
assert swim(pools.list('std::deque<float>'))
assert swim(pools.list('std::string'))

assert swim(
    Function.Behaviour()(src)
)

swim.write('example.i')
print('ok!')
