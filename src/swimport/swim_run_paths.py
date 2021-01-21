import os
import sys
from swimport.swim_run import swimport_paths_tuple


def get_path_set(paths_set=0, python_major=3, python_minor=7) -> swimport_paths_tuple:
    PYTHON_ROOT = os.path.dirname(sys.executable)
    SWIG_PATH = r'd:\dev\swigwin-3.0.12\swig.exe'
    if not paths_set:
        windows_kit_template = r'C:\Program Files (x86)\Windows Kits\10\{}\10.0.17763.0' + "\\"
        MSVC_dir = r'C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Tools\MSVC\14.16.27023' + "\\"
    else:
        windows_kit_template = r'C:\Program Files (x86)\Windows Kits\10\{}\10.0.18362.0' + "\\"
        MSVC_dir = r'c:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Tools\MSVC\14.26.28801' + "\\"

    np_include_path = PYTHON_ROOT + r"\Lib\site-packages\numpy\core\include\\"
    PY_INCLUDE_PATH = PYTHON_ROOT + r'\include'
    PY_LIB_PATH = PYTHON_ROOT + r'\libs\python{}{}.lib'.format(python_major, python_minor)

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
    return swimport_paths_tuple(
        SWIG_PATH, PYTHON_ROOT, windows_kit_template, MSVC_dir, np_include_path, PY_INCLUDE_PATH,
        PY_LIB_PATH, windows_kit_include, windows_kit_lib, CL_PATH, COMPILE_ADDITIONAL_INCLUDE_DIRS,
        COMPILE_ADDITIONAL_LIBS)
