from swimport import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))
swim(pools.include('../resources/cpp_iterable.h'))

swim(pools.primitive)
swim(pools.std_string)
swim(pools.c_string)

swim(pools.tuple('char', 'int'))
swim(pools.tuple('int', 'int'))
swim(pools.tuple())
swim(pools.tuple('std::tuple<>'))

assert swim(
    ('person' >> Container.Behaviour())(src)
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
                    """)
)

swim(pools.tuple('person', 'wchar_t const *', 'point'))

assert swim(
    Function.Behaviour()(src)
)

swim.write('example.i')
print('ok!')
