from swimport.all import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))
swim(pools.std_string)

cswim = ContainerSwim('Polynomial', src)

cswim((Function.Trigger() > Function.Trigger('operator=')) >> Function.Behaviour())
cswim.extend_method("Polynomial __rmul__(double s);", "{return (*$self)*Polynomial(s);}")
cswim.extend_method("Polynomial __mul__(double s);", "{return (*$self)*Polynomial(s);}")
cswim.extend_method("Polynomial __radd__(double s);", "{return (*$self)+Polynomial(s);}")
cswim.extend_method("Polynomial __add__(double s);", "{return (*$self)+Polynomial(s);}")
cswim.extend_method("Polynomial __sub__(double s);", "{return (*$self)-Polynomial(s);}")
cswim.extend_method("Polynomial __rsub__(double s);", "{return Polynomial(s)-(*$self);}")
cswim.extend_py_def("__pow__", 'self, pow',
                    """
                    if pow == 0:
                        return type(self)(1)
                    if pow == 1:
                        return self
                    if pow%2 == 0:
                        temp = self**(pow//2)
                        return temp*temp
                    return self * (self**(pow-1))
                    """)
cswim.extend_py_def("__call__", 'self, *args',
                    """
                    if len(args) == 1:
                        try:
                            args = iter(args[0])
                        except TypeError:
                            return self.__call__.prev(self, args[0])
                    return [self.__call__.prev(self, a) for a in args]
                    """)
cswim.extend_py_def("__truediv__", 'self, other',
                    """
                    return self * (1/other)
                    """)
cswim.extend_py_def('from_points', 'cls, points',
                    """
                    ret = cls()
                    x = cls(1,1)
                    for i,(x_i,y_i) in enumerate(points):
                        lang = 1
                        for j,(x_j,y_j) in enumerate(points):
                            if i == j:
                                continue
                            lang *= (x-x_j) / (x_i-x_j)
                        ret += cls(y_i) * lang
                    return ret
                    """, wrapper='classmethod')
cswim(... >> Variable.Behaviour())

assert swim(cswim)

swim.write('example.i')
print('ok!')
