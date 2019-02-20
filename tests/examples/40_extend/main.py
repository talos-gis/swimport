from swimport import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))
swim(pools.std_string)

cswim = ContainerSwim('Polynomial', src)

cswim(... >> Function.Behaviour())
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
cswim.extend_py_def("exponential_points", 'self',
                    """
                    abs_x = 1
                    while True:
                        yield abs_x, self(abs_x)
                        yield -abs_x, self(-abs_x)
                        abs_x *= 2
                    """)

assert swim(cswim)

assert swim(Variable.Behaviour()(src))

swim.write('example.i')
print('ok!')
