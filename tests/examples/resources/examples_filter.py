from typing import Container, Union
from tests.examples.resources.filter import Filter, All
from pathlib import Path
import warnings
import re

derived_types = All[26:33, 34, 45, 49]
types = All[3:9, 21:24] & derived_types
containers = All[6:9, 37:45, 46:49]
arrays = All[14:16, 36]
strings = All[16:18, 19:21]
typedefs = All[9:11]
enums = All[11, 13]
variables = All[5, 42]

# if you only want to run one example, put its number here
filter_: Union[int, Filter] = All

if isinstance(filter_, Container):
    pass
elif isinstance(filter_, int):
    filter_ = (filter_,)
else:
    raise Exception('filter not recognised')

example_number_pattern = re.compile(r'0*(?P<num>[0-9]+)_')


if filter_ is not All:
    warnings.warn(f'warning: a filter {filter_!r} is in place, only a limited number of tests will run',
                  stacklevel=10)


def passes_filter(path: Path):
    match = example_number_pattern.match(path.name)
    if not match:
        return False
    num = int(match.group('num'))
    return num in filter_

