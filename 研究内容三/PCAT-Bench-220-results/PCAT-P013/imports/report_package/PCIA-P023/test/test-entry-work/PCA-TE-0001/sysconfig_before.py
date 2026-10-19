"""Access to Python's configuration information."""

import os
import sys
import threading
from os.path import realpath

__all__ = [
    'get_config_h_filename',
    'get_config_var',
    'get_config_vars',
    'get_makefile_filename',
    'get_path',
    'get_path_names',
    'get_paths',
    'get_platform',
    'get_python_version',
    'get_scheme_names',
    'parse_config_h',
]

# Keys for get_config_var() that are never converted to Python integers.
_ALWAYS_STR = {
    'IPHONEOS_DEPLOYMENT_TARGET',
    'MACOSX_DEPLOYMENT_TARGET',
}

_INSTALL_SCHEMES = {
    'posix_prefix': {
        'stdlib': '{installed_base}/{platlibdir}/{implementation_lower}{py_version_short}{abi_thread}',
        'platstdlib': '{platbase}/{platlibdir}/{implementation_lower}{py_version_short}{abi_thread}',
        'purelib': '{base}/lib/{implementation_lower}{py_version_short}{abi_thread}/site-packages',
        'platlib': '{platbase}/{platlibdir}/{implementation_lower}{py_version_short}{abi_thread}/site-packages',
        'include':
            '{installed_base}/include/{implementation_lower}{py_version_short}{abiflags}',
        'platinclude':
            '{installed_platbase}/include/{implementation_lower}{py_version_short}{abiflags}',
        'scripts': '{base}/bin',
        'data': '{base}',
        },
    'posix_home': {
        'stdlib': '{installed_base}/lib/{implementation_lower}',
        'platstdlib': '{base}/lib/{implementation_lower}',
        'purelib': '{base}/lib/{implementation_lower}',
        'platlib': '{base}/lib/{implementation_lower}',
        'include': '{installed_base}/include/{implementation_lower}',
        'platinclude': '{installed_base}/include/{implementation_lower}',
        'scripts': '{base}/bin',
        'data': '{base}',
        },
    'nt': {
        'stdlib': '{installed_base}/Lib',
        'platstdlib': '{base}/Lib',
        'purelib': '{base}/Lib/site-packages',
        'platlib': '{base}/Lib/site-packages',
        'include': '{installed_base}/Include',
        'platinclude': '{installed_base}/Include',
        'scripts': '{base}/Scripts',
        'data': '{base}',
        },

    # Downstream distributors can overwrite the default install scheme.
    # This is done to support downstream modifications where distributors change
    # the installation layout (eg. different site-packages directory).
    # So, distributors will change the default scheme to one that correctly
    # represents their layout.
    # This presents an issue for projects/people that need to bootstrap virtual
    # environments, like virtualenv. As distributors might now be customizing
    # the default install scheme, there is no guarantee that the information
    # returned by sysconfig.get_default_scheme/get_paths is correct for
    # a virtual environment, the only guarantee we have is that it is correct
    # for the *current* environment. When bootstrapping a virtual environment,
    # we need to know its layout, so that we can place the files in the
    # correct locations.
    # The "*_venv" install scheme is a scheme to bootstrap virtual environments,
    # essentially identical to the default posix_prefix/nt schemes.
    # Downstream distributors who patch posix_prefix/nt scheme are encouraged to
    # leave the following schemes unchanged
    'posix_venv': {
        'stdlib': '{installed_base}/{platlibdir}/{implementation_lower}{py_version_short}{abi_thread}',
        'platstdlib': '{platbase}/{platlibdir}/{implementation_lower}{py_version_short}{abi_thread}',
        'purelib': '{base}/lib/{implementation_lower}{py_version_short}{abi_thread}/site-packages',
        'platlib': '{platbase}/{platlibdir}/{implementation_lower}{py_version_short}{abi_thread}/site-packages',
        'include':
            '{installed_base}/include/{implementation_lower}{py_version_short}{abiflags}',
        'platinclude':
            '{installed_platbase}/include/{implementation_lower}{py_version_short}{abiflags}',
        'scripts': '{base}/bin',
        'data': '{base}',
        },
    'nt_venv': {
        'stdlib': '{installed_base}/Lib',
        'platstdlib': '{base}/Lib',
        'purelib': '{base}/Lib/site-packages',
        'platlib': '{base}/Lib/site-packages',
        'include': '{installed_base}/Include',
        'platinclude': '{installed_base}/Include',
        'scripts': '{base}/Scripts',
        'data': '{base}',
        },
    }

# For the OS-native venv scheme, we essentially provide an alias:
if os.name == 'nt':
    _INSTALL_SCHEMES['venv'] = _INSTALL_SCHEMES['nt_venv']
else:
    _INSTALL_SCHEMES['venv'] = _INSTALL_SCHEMES['posix_venv']

def _get_implementation():
    return 'Python'

# NOTE: site.py has copy of this function.
# Sync it when modify this function.
def _getuserbase():
    env_base = os.environ.get("PYTHONUSERBASE", None)
    if env_base:
        return env_base

    # Emscripten, iOS, tvOS, VxWorks, WASI, and watchOS have no home directories.
    # Use _PYTHON_HOST_PLATFORM to get the correct platform when cross-compiling.
    system_name = os.environ.get('_PYTHON_HOST_PLATFORM', sys.platform).split('-')[0]
    if system_name in {"emscripten", "ios", "tvos", "vxworks", "wasi", "watchos"}:
        return None

    def joinuser(*args):
        return os.path.expanduser(os.path.join(*args))

    if os.name == "nt":
        base = os.environ.get("APPDATA") or "~"
        return joinuser(base,  _get_implementation())

    if sys.platform == "darwin" and sys._framework:
        return joinuser("~", "Library", sys._framework,
                        f"{sys.version_info[0]}.{sys.version_info[1]}")

    return joinuser("~", ".local")

_HAS_USER_BASE = (_getuserbase() is not None)

if _HAS_USER_BASE:
    _INSTALL_SCHEMES |= {
        # NOTE: When modifying "purelib" scheme, update site._get_path() too.
        'nt_user': {
            'stdlib': '{userbase}/{implementation}{py_version_nodot_plat}',
            'platstdlib': '{userbase}/{implementation}{py_version_nodot_plat}',
            'purelib': '{userbase}/{implementation}{py_version_nodot_plat}/site-packages',
            'platlib': '{userbase}/{implementation}{py_version_nodot_plat}/site-packages',
            'include': '{userbase}/{implementation}{py_version_nodot_plat}/Include',
            'scripts': '{userbase}/{implementation}{py_version_nodot_plat}/Scripts',
            'data': '{userbase}',
            },
        'posix_user': {
            'stdlib': '{userbase}/{platlibdir}/{implementation_lower}{py_version_short}{abi_thread}',
            'platstdlib': '{userbase}/{platlibdir}/{implementation_lower}{py_version_short}{abi_thread}',
            'purelib': '{userbase}/lib/{implementation_lower}{py_version_short}{abi_thread}/site-packages',
            'platlib': '{userbase}/lib/{implementation_lower}{py_version_short}{abi_thread}/site-packages',
            'include': '{userbase}/include/{implementation_lower}{py_version_short}{abi_thread}',
            'scripts': '{userbase}/bin',
            'data': '{userbase}',
            },
        'osx_framework_user': {
            'stdlib': '{userbase}/lib/{implementation_lower}',
            'platstdlib': '{userbase}/lib/{implementation_lower}',
            'purelib': '{userbase}/lib/{implementation_lower}/site-packages',
            'platlib': '{userbase}/lib/{implementation_lower}/site-packages',
            'include': '{userbase}/include/{implementation_lower}{py_version_short}',
            'scripts': '{userbase}/bin',
            'data': '{userbase}',
            },
    }

_SCHEME_KEYS = ('stdlib', 'platstdlib', 'purelib', 'platlib', 'include',
                'scripts', 'data')

_PY_VERSION = sys.version.split()[0]
_PY_VERSION_SHORT = f'{sys.version_info[0]}.{sys.version_info[1]}'
_PY_VERSION_SHORT_NO_DOT = f'{sys.version_info[0]}{sys.version_info[1]}'
_BASE_PREFIX = os.path.normpath(sys.base_prefix)
_BASE_EXEC_PREFIX = os.path.normpath(sys.base_exec_prefix)
# Mutex guarding initialization of _CONFIG_VARS.
_CONFIG_VARS_LOCK = threading.RLock()
_CONFIG_VARS = None
# True iff _CONFIG_VARS has been fully initialized.
_CONFIG_VARS_INITIALIZED = False
_USER_BASE = None


def _safe_realpath(path):
    try:
        return real