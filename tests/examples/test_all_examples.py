from typing import Container, Union

from pathlib import Path
import os
import sys
import itertools as it
import subprocess
import warnings
import re

from tests.examples.resources.filter import Filter, All

SWIG_PATH = r'd:\git\swigwin-3.0.12\swig.exe'
PY_INCLUDE_PATH = r'C:\python_envs\x64\3.7\include'
PY_LIB_PATH = r'C:\python_envs\x64\3.7\libs\python37.lib'

windows_kit_template = r'C:\Program Files (x86)\Windows Kits\10\{}\10.0.17763.0' + "\\"
MSVC_dir = r'C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Tools\MSVC\14.16.27023' + "\\"
np_include_path = r"C:\python_envs\x64\3.7\Lib\site-packages\numpy\core\include\\"
windows_kit_include = windows_kit_template.format('include')
windows_kit_lib = windows_kit_template.format('lib')

CL_PATH = MSVC_dir + r'bin\Hostx64\x64\cl.exe'
COMPILE_ADDITIONAL_INCLUDE_DIRS = [
    MSVC_dir + 'include',
    windows_kit_include + 'ucrt',
    windows_kit_include + 'shared',
    windows_kit_include + 'um',
    np_include_path
]
COMPILE_ADDITIONAL_LIBS = [
    MSVC_dir + r'lib\x64\libcpmt.lib',
    MSVC_dir + r'lib\x64\libcmt.lib',
    MSVC_dir + r'lib\x64\oldnames.lib',
    MSVC_dir + r'lib\x64\libvcruntime.lib',
    windows_kit_lib + r'um\x64\kernel32.lib',
    windows_kit_lib + r'ucrt\x64\libucrt.lib',
    windows_kit_lib + r'um\x64\Uuid.lib'
]

# region filter categories
derived_types = All[26:33, 34, 45, 49]
types = All[3:9, 21:24] & derived_types
containers = All[6:9, 37:45, 46:49]
arrays = All[14:16, 36]
strings = All[16:18, 19:21]
typedefs = All[9:11]
enums = All[11, 13]
variables = All[5, 42]
# endregion

# if you only want to run one example, put its number here
filter_: Union[int, Filter] = All
# if things are compiling weird, first thing, change this to /Od
optimization = '/O2'

"""
An open letter to the c++ compiler:
Dear c++ compiler,
I get that performance is paramount, I get it. turning this:
return add(x,y);

into

return x+y;
is all well and good, but turning this:
auto x = A()
B;
return x;

into:
B;
return A();

is terrible, and leads to the worst bugs imaginable. So thank you c++ compiler. Thank you for thinking that time travel
is okay, you are the sole reason that the keyword `volatile` appears almost as much as `const`.

yours faithfully- now and until rust has normal overloads,
Ben
"""

if isinstance(filter_, Container):
    pass
elif isinstance(filter_, int):
    filter_ = (filter_,)
else:
    raise Exception('filter not recognised')

example_number_pattern = re.compile(r'0*(?P<num>[0-9]+)_')


def passes_filter(path: Path):
    match = example_number_pattern.match(path.name)
    if not match:
        return False
    num = int(match.group('num'))
    return num in filter_


def run_example(dirname: Path, show=True):
    original_cwd = os.getcwd()
    os.chdir(str(dirname.absolute()))

    main_path = dirname / 'main.py'
    inter_path = dirname / 'example.i'
    cxx_path = dirname / 'example_wrap.cxx'
    usage_path = dirname / 'usage.py'

    if main_path.exists():
        if show:
            print('\t' + 'main.py', end='...', flush=True)
        subprocess.run([sys.executable, 'main.py'],
                       stdout=subprocess.PIPE, check=True)
        if show:
            print('done!')
    elif show:
        print('\tmain.py missing')

    if inter_path.exists():
        if show:
            print('\t' + 'example.i', end='...', flush=True)
        subprocess.run([SWIG_PATH, '-c++', '-python', '-py3',  # '-debug-tmsearch',
                        '-outdir', str(dirname), str(inter_path)],
                       stdout=None, check=True)
        if show:
            print('done!')
    elif show:
        print('\texample.i missing')

    if cxx_path.exists():
        if show:
            print('\t' + 'example_wrap.cxx', end='...', flush=True)
        tmpdir = dirname / 'temp'
        src_path = dirname / 'src.cpp'

        tmpdir.mkdir(exist_ok=True, parents=True)
        # todo compile with warnings?
        proc = subprocess.run([
            CL_PATH, '/nologo', '/LD', '/EHsc', '/utf-8', optimization,
            '/Tp', str(cxx_path),
            *(('/Tp', str(src_path)) if src_path.exists() else ()),
            '/Fo:' + str(tmpdir) + '\\',
            '/I', PY_INCLUDE_PATH,
            '/I', str(dirname),
            *it.chain.from_iterable(('/I', i) for i in COMPILE_ADDITIONAL_INCLUDE_DIRS),
            '/link',
            '/LIBPATH', PY_LIB_PATH,
            *it.chain.from_iterable(('/LIBPATH', l) for l in COMPILE_ADDITIONAL_LIBS),
            '/IMPLIB:' + str(tmpdir / 'example.lib'),
            '/OUT:' + str(dirname / '_example.pyd')
        ], stdout=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            print(proc.stdout)
            raise Exception(f'cl returned {proc.returncode}')
        if show:
            print('done!')
    elif show:
        print('\texample_wrap.cxx missing')

    if usage_path.exists():
        if show:
            print('\t' + 'usage.py', end='...', flush=True)
        subprocess.run([sys.executable, 'usage.py'],
                       stdout=None, stderr=None, check=True
                       )
        if show:
            print('done!')
    elif show:
        print('\tusage.py missing')

    os.chdir(original_cwd)


def main():
    if filter_ is not All:
        warnings.warn(f'warning: a filter {filter_!r} is in place, only a limited number of tests will run',
                      stacklevel=10)
    if optimization != '/O2':
        warnings.warn(f'warning: optimization should be set to maximum (/O2 instead of {optimization}),'
                      'to ensure completeness',
                      stacklevel=10)
    tests_dir = Path.cwd()
    for item in tests_dir.iterdir():
        if not passes_filter(item):
            continue
        print(str(item.name) + ':')
        run_example(item)


if __name__ == '__main__':
    main()
