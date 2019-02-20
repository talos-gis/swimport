from swimport import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))

assert swim(
    TypeSwimporting('Point',
                    to_py="""
                    return Py_BuildValue("dd",input.x, input.y);
                    """,
                    to_cpp="""
                    double x, y;
                    if (!PyArg_ParseTuple(input, "dd",&x, &y)) {ok=false; return {};}
                    return{x,y};
                    """)
)

cswim = ContainerSwim('LineSegment', src)

assert cswim('angle' >> FunctionBehaviour())

assert swim(cswim)

swim.write('example.i')
print('ok!')
