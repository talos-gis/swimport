from setuptools import setup

from swimport_data import (
    __name__,
    __author__,
    __author_email__,
    __license__,
    __url__,
    __version__,
)

setup(
    name=__name__,
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    license=__license__,
    url=__url__,
    packages=['swimport', 'swimport.model', 'swimport.pools', 'swimport_data', 'swimport.pools.derived_types'],
    install_requires=['CppHeaderParser>=2', ],
    python_requires='>=3.6.0',
    include_package_data=True,
    data_files=[
        ('', ['README.md', 'CHANGELOG.md']),
    ],
    extras_require={
        'memory testing': ['psutil']
    },
)
