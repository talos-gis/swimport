import os
import sys
from swimport.swim_run import swimport_paths_tuple


def get_path_set(python_ver=None, msvc=2019, msvc_pro=True, win10_sdk='10.0.18362.0') -> swimport_paths_tuple:
    if python_ver is None:
        python_ver = sys.version_info
    PYTHON_ROOT = os.path.dirname(sys.executable)
    SWIG_PATH = r'd:\dev\swigwin-3.0.12\swig.exe'
    windows_kit_template = r'C:\Program Files (x86)\Windows Kits\10\{}' + '\\' + win10_sdk + '\\'
    msvc_dir = None
    if msvc == 2019:
        msvc_dir = r'c:\Program Files (x86)\Microsoft Visual Studio\2019\{}\VC\Tools\MSVC\14.28.29333' + '\\'
    elif msvc == 2017:
        msvc_dir = r'C:\Program Files (x86)\Microsoft Visual Studio\2017\{}\VC\Tools\MSVC\14.16.27023' + '\\'
    if msvc_dir is None:
        msvc_dir = msvc
    else:
        msvc_dir = msvc_dir.format('Professional' if msvc_pro else 'Community')

    np_include_path = PYTHON_ROOT + r"\Lib\site-packages\numpy\core\include\\"
    PY_INCLUDE_PATH = PYTHON_ROOT + r'\include'
    PY_LIB_PATH = PYTHON_ROOT + r'\libs\python{}{}.lib'.format(python_ver[0], python_ver[1])

    windows_kit_include = windows_kit_template.format('include')
    windows_kit_lib = windows_kit_template.format('lib')

    CL_PATH = msvc_dir + r'bin\Hostx64\x64\cl.exe'
    COMPILE_ADDITIONAL_INCLUDE_DIRS = [
        msvc_dir + 'include',
        windows_kit_include + 'ucrt',
        windows_kit_include + 'shared',
        windows_kit_include + 'um',
        np_include_path
    ]
    COMPILE_ADDITIONAL_LIBS = [
        msvc_dir + r'lib\x64\libcpmt.lib',
        msvc_dir + r'lib\x64\libcmt.lib',
        msvc_dir + r'lib\x64\oldnames.lib',
        msvc_dir + r'lib\x64\libvcruntime.lib',
        windows_kit_lib + r'um\x64\kernel32.lib',
        windows_kit_lib + r'ucrt\x64\libucrt.lib',
        windows_kit_lib + r'um\x64\Uuid.lib'
    ]
    return swimport_paths_tuple(
        SWIG_PATH, PYTHON_ROOT, windows_kit_template, msvc_dir, np_include_path, PY_INCLUDE_PATH,
        PY_LIB_PATH, windows_kit_include, windows_kit_lib, CL_PATH, COMPILE_ADDITIONAL_INCLUDE_DIRS,
        COMPILE_ADDITIONAL_LIBS)
