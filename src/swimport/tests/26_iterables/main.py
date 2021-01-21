from swimport.all import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))
swim(pools.primitive)
swim(pools.c_string)

assert swim(
    TypeSwimporting('point',
                    to_py="""
                    return Py_BuildValue("ii",input.x, input.y);
                    """,
                    to_cpp="""
                    int x, y;
                    if (!PyArg_ParseTuple(input, "ii",&x, &y)) ok=false;
                    return {x,y};
                    """)
)

assert swim(
    ('person' >> Container.Behaviour())(src)
)

assert swim(
    Function.Behaviour(exception_check=...)(src)
)

swim.write('example.i')
print('ok!')
