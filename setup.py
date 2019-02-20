import setuptools

import swimport

setuptools.setup(
    name=swimport.__name__,
    version=swimport.__version__,
    author=swimport.__author__,
    packages=['swimport', ],
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
