from swimport import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))

point_type = TypeSwimporting('Point2D', 'Tuple[float, float]',
                             to_py=
                             """
                             return Py_BuildValue("dd",input.x,input.y);
                             """,
                             to_cpp=
                             """
                              double x,y;
                              PyArg_ParseTuple(input,"dd",&x,&y);
                              return{x,y};
                             """, out_iterable_types=())
assert swim(point_type)
assert swim(pools.list('Point2D'))
assert swim(Variable.Behaviour()(src)) == 3
assert swim(Function.Behaviour()(src))

swim.write('example.i')
print('ok!')
