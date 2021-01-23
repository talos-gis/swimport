from setuptools import setup, find_packages

from src.swimport import (
    __pacakge_name__,
    __author__,
    __author_email__,
    __maintainer__,
    __maintainer_email__,
    __license__,
    __url__,
    __version__,
    __description__,
)

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Environment :: Win32 (MS Windows)',
    'Programming Language :: Python :: 3',
]

__readme__ = open('README.md', encoding="utf-8").read()
__readme_type__ = 'text/markdown'

package_root = 'src'   # package sources are under this dir
packages = find_packages(package_root)  # include all packages under package_root
package_dir = {'': package_root}  # packages sources are under package_root

setup(
    name=__pacakge_name__,
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    maintainer=__maintainer__,
    maintainer_email=__maintainer_email__,
    license=__license__,
    url=__url__,
    long_description=__readme__,
    long_description_content_type=__readme_type__,
    description=__description__,
    classifiers=classifiers,
    packages=packages,
    package_dir=package_dir,
    install_requires=['CppHeaderParser>=2'],
    extras_require={
        'memory testing': ['psutil']
    },
    python_requires=">=3.6.0",
)
