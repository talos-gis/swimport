from swimport.all import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))
swim(pools.include('../resources/cpp_iterable.h'))
swim(pools.primitive)
swim(pools.std_string)

cswim = ContainerSwim('Polynomial', src)
cswim.extend_method("static Polynomial from_roots(std::vector<double> s);",
                    """
                    {
                        Polynomial ret = 1;
                        for (auto root: s){
                            ret = ret * (x-root);
                        }
                        return ret;
                    }
                    """)
cswim.extend_method("static std::vector<Polynomial> pows(int n);",
                    """
                    {
                        std::vector<Polynomial> ret;
                        Polynomial current = 1;
                        Polynomial x = {1,1};
                        for(auto i = 0; i<n;i++){
                            ret.push_back(current);
                            current = current * x;
                        }
                        return ret;
                    }
                    """)
cswim.extend_py_def('from_roots', '*args',
                    """
                    def flatten(it):
                        for i in it:
                            try:
                                yield from i
                            except TypeError:
                                yield i
                    return Polynomial.from_roots.prev(flatten(args))
                    """)
cswim.extend_py_def('from_points', 'cls, points',
                    """
                    ret = cls()
                    x = cls(1,1)
                    for i,(x_i,y_i) in enumerate(points):
                        lang = cls(1)
                        for j,(x_j,y_j) in enumerate(points):
                            if i == j:
                                continue
                            lang *= (x-cls(x_j)) * cls(1/(x_i-x_j))
                        ret += cls(y_i) * lang
                    return ret
                    """, wrapper='classmethod')

cswim(... >> FunctionBehaviour())
assert swim(cswim)

assert swim(Variable.Behaviour()(src))

swim.write('example.i')
print('ok!')
