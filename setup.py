#!/usr/bin/env python
import os
import subprocess

from setuptools import setup
from setuptools.command.build_py import build_py


class BuildPyDepCdll(build_py):
    def run(self):
        super().run()
        subprocess.check_call(['bash', './make_sharedlib.sh'])


def get_pkg_version_scheme(
    default_ver_scheme: str = 'no-guess-dev',
    default_loc_scheme: str = 'node-and-date'
) -> dict:
    """Get package version scheme from the environment.

    Parameters
    ----------
    default_ver_scheme : str, optional
        Fallback default version scheme for the package
        (default is 'no-guess-dev').
    default_loc_scheme : str, optional
        Fallback default local scheme for the package
        (default is 'node-and-date').

    Returns
    -------
    dict
        Package version scheme(s).

    See Also
    --------
    :pkg:`setuptools_scm`
        For available version schemes.

    """
    ver_scheme = os.getenv('PY_SCM_VER_SCHEME', '').strip() \
        or default_ver_scheme
    loc_scheme = os.getenv('PY_SCM_LOC_SCHEME', '').strip() \
        or default_loc_scheme

    return {
        'version_scheme': ver_scheme,
        'local_scheme': loc_scheme,
    }


if __name__ == '__main__':
    setup(
        use_scm_version=get_pkg_version_scheme(),
        cmdclass={'build_py': BuildPyDepCdll},
    )
