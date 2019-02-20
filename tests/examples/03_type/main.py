from swimport import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))

point_type = TypeSwimporting('Point3D', 'Tuple[float, float, float]',
                             to_py=
                             """
                             return Py_BuildValue("ddd",input.x,input.y,input.z);
                             """,
                             to_cpp=
                             """
                              double x,y,z=0;
                              PyArg_ParseTuple(input,"dd|d",&x,&y, &z);
                              /* note: we don't need to check for an error here, the python error will be detected
                              and result in a standard failure */
                              return {x,y,z};
                             """,)
assert swim(point_type)
assert swim(Function.Behaviour()(src))

swim.write('example.i')
print('ok!')
