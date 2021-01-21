from swimport.all import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))
swim(pools.include('../resources/cpp_iterable.h'))

swim(pools.primitive)
swim(pools.std_string)
swim(pools.c_string)

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

swim(pools.map('int', 'int', output=iter))
swim(pools.map('wchar_t', 'int', output=list))
swim(pools.map('std::string', 'point', output=iter))
swim(pools.map('int', 'point', output=iter))

assert swim(
    Function.Behaviour()(src)
)

swim.write('example.i')
print('ok!')
