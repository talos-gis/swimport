import swimport.pools.types
import swimport.pools.derived_types
import swimport.pools.complex_types
from swimport.pools.pools import pools, Pool, syspools

del types, derived_types, complex_types

pools.auto_build_doc = True
pools.rebuild_doc()