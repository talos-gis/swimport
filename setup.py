import setuptools

import swimport_data

setuptools.setup(
    name=swimport_data.__name__,
    version=swimport_data.__version__,
    author=swimport_data.__author__,
    packages=['swimport', 'swimport.model', 'swimport.pools', 'swimport_data'],
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
