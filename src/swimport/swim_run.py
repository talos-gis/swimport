from pathlib import Path
import os
import sys
import itertools as it
import subprocess
import warnings
import ntpath
import glob
from collections import namedtuple

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


fields = ('SWIG_PATH', 'PYTHON_ROOT', 'windows_kit_template', 'MSVC_dir', 'np_include_path', 'PY_INCLUDE_PATH',
          'PY_LIB_PATH', 'windows_kit_include', 'windows_kit_lib', 'CL_PATH', 'COMPILE_ADDITIONAL_INCLUDE_DIRS',
          'COMPILE_ADDITIONAL_LIBS')

swimport_paths_tuple = namedtuple('swimport_paths', fields)


def swim_run(
        dirname: Path,
        swimport_paths: swimport_paths_tuple,
        optimization,
        print_out=True, module_name=..., is_cpp=...):
    original_cwd = os.getcwd()
    os.chdir(str(dirname.absolute()))

    if module_name is ...:
        files = glob.glob(str(dirname / '*.m'))
        if files:
            head, tail = ntpath.split(files[0])
            parts = tail.split('.')
            module_name = parts[0]
            if is_cpp is ...:
                is_cpp = 'c' not in parts
        else:
            module_name = 'example'
    if is_cpp is ...:
        is_cpp = True

    cxx_ext = '.cxx' if is_cpp else '.c'
    src_ext = '.cpp' if is_cpp else '.c'

    main_path = dirname / 'main.py'
    inter_path = dirname / Path(module_name+'.i')
    cxx_path = dirname / (module_name+'_wrap'+cxx_ext)
    usage_path = dirname / 'usage.py'

    if main_path.exists():
        if print_out:
            print('\t' + 'main.py', end='...', flush=True)
        subprocess.run([sys.executable, 'main.py', module_name],
                       stdout=subprocess.PIPE, check=True)
        if print_out:
            print('done!')
    elif print_out:
        print('\tmain.py missing')

    if inter_path.exists():
        if print_out:
            print('\t' + module_name+'.i', end='...', flush=True)
        popenargs = [swimport_paths.SWIG_PATH]
        if is_cpp:
            popenargs.append('-c++')
        popenargs.extend(['-python', '-py3'])
        # popenargs.append('-debug-tmsearch')
        popenargs.extend(['-outdir', str(dirname), str(inter_path)])

        subprocess.run(popenargs, check=True)
        if print_out:
            print('done!')
    elif print_out:
        print('\t'+module_name+'.i missing')

    if cxx_path.exists():
        if print_out:
            print('\t' + str(cxx_path), end='...', flush=True)
        tmpdir = dirname / 'temp'
        src_path = dirname / Path('src'+src_ext)

        tmpdir.mkdir(exist_ok=True, parents=True)
        # todo compile with warnings?

        is_64bits = sys.maxsize > 2 ** 32
        pyd_suffix = f'.cp{sys.version_info[0]}{sys.version_info[1]}-{"win_amd64" if is_64bits else "win32"}.pyd'

        proc = subprocess.run([
            swimport_paths.CL_PATH, '/nologo', '/LD', '/EHsc', '/utf-8', optimization,
            '/Tp', str(cxx_path),
            *(('/Tp', str(src_path)) if src_path.exists() else ()),
            '/Fo:' + str(tmpdir) + '\\',
            '/I', swimport_paths.PY_INCLUDE_PATH,
            '/I', str(dirname),
            *it.chain.from_iterable(('/I', i) for i in swimport_paths.COMPILE_ADDITIONAL_INCLUDE_DIRS),
            '/link',
            '/LIBPATH', swimport_paths.PY_LIB_PATH,
            *it.chain.from_iterable(('/LIBPATH', l) for l in swimport_paths.COMPILE_ADDITIONAL_LIBS),
            '/IMPLIB:' + str(tmpdir / Path(module_name+'.lib')),
            '/OUT:' + str(dirname / Path('_'+module_name+pyd_suffix))
        ], stdout=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            print(proc.stdout)
            raise Exception(f'cl returned {proc.returncode}')
        if print_out:
            print('done!')
    elif print_out:
        print('\t'+str(cxx_path)+' missing')

    if usage_path.exists():
        if print_out:
            print('\t' + 'usage.py', end='...', flush=True)
        subprocess.run([sys.executable, 'usage.py'],
                       stdout=None, stderr=None, check=True
                       )
        if print_out:
            print('done!')
    elif print_out:
        print('\tusage.py missing')

    os.chdir(original_cwd)


def simple_passes_filter(path: Path):
    head, tail = ntpath.split(path)
    return not tail.startswith('_')


def swim_run_subfolders(root_dir, optimization, passes_filter, **kwargs):
    if optimization != '/O2':
        warnings.warn(f'warning: optimization should be set to maximum (/O2 instead of {optimization}),'
                      'to ensure completeness',
                      stacklevel=10)
    for item in root_dir.iterdir():
        if not item.is_dir() or not passes_filter(item):
            continue
        print(str(item.name) + ':')
        swim_run(item, optimization=optimization, **kwargs)
