from swimport import *

src = FileSource('src.h')
swim = Swim('example')
swim(pools.include(src))

assert swim(('factorial' >> Function.Behaviour(contract="""require:\ni >= 0;"""))(src))
assert swim(('inv' >> Function.Behaviour(contract="""require:\nx;"""))(src))
assert swim(('sign' >> Function.Behaviour(contract="""ensure:\n(sign == 0 || sign == 1 || sign == -1)"""))(src))

swim.write('example.i')
print('ok!')
