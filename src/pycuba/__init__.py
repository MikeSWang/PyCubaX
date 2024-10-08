#!/usr/bin/env python
"""
PyCuba(X): a new Python wrapper for the Cuba library
===========================================

The ``Cuba`` library offers a choice of four independent routines for
multidimensional numerical integration: Vegas, Suave, Divonne, and Cuhre.
It is written by `Thomas Hahn <https://wwwth.mpp.mpg.de/members/hahn/>`_
and is available at `<http://www.feynarts.de/cuba/>`_
under the LGPLv3 licence.

The ``PyCuba`` package provides a Python wrapper for the ``Cuba`` library.
It is written by `Johannes Buchner <https://github.com/JohannesBuchner>`_
and is available as part of |PyMultiNest|_ under the GPLv3 licence.

Both libraries/packages have been modified and redistributed here under
the GLPv3+ licence.

.. codeauthor:: Johannes Buchner <https://github.com/JohannesBuchner>

.. codeauthor:: Mike S Wang <https://github.com/MikeSWang>

.. |PyMultiNest| replace:: ``PyMultiNest``

.. _PyMultiNest: https://github.com/JohannesBuchner/PyMultiNest

"""
import os
import platform
from collections.abc import Callable
from ctypes import (
    CDLL,
    CFUNCTYPE,
    POINTER,
    Structure,
    _CFuncPtr,
    _Pointer,
    byref,
    cdll,
    c_double,
    c_int,
    c_void_p
)
from importlib.metadata import PackageNotFoundError, version


# ========================================================================
# Metadata
# ========================================================================

__copyright__ = 'Copyright (C) 2024 Johannes Buchner & Mike S Wang'
__date__ = '2024-10-07'
__license__ = 'GPL-3.0-or-later'

try:
    __version__ = version('pycubax')
except PackageNotFoundError:
    __version__ = 'cuba-4.2.2'  # fallback version number


# ========================================================================
# Dynamic library
# ========================================================================

# Disable parallelisation within Cuba: Python does not know that the call
# is in parallel and writes to the same memory location, causing overrides;
# this could be overcome by using locks.
os.environ['CUBACORES'] = '0'

# Load the Cuba library.
_module_dir: str = os.path.dirname(os.path.abspath(__file__))
_dist_dir: str = os.path.join(_module_dir, "../../dist")

if platform.system() == 'Darwin':
    _lib_suffix: str = '.dylib'
elif platform.system() == 'Linux':
    _lib_suffix: str = '.so'
else:
    raise OSError(f"Unsupported OS: {platform.system()}")

_libcuba_file = 'libcuba' + _lib_suffix
_libcuba_path_repo: str = os.path.join(_dist_dir, _libcuba_file)
_libcuba_path_explicit: str = os.getenv('LIBCUBA', _libcuba_path_repo)

_libcuba_source: str = ""

libcuba: CDLL = None
"""Cuba library object."""

try:
    # Load from the system's search paths.
    libcuba = cdll.LoadLibrary(_libcuba_file)
    _libcuba_source = f"{libcuba._name} (system)"
except OSError:
    # Load from the explicit path.
    try:
        libcuba = cdll.LoadLibrary(_libcuba_path_explicit)
        _libcuba_source = os.path.abspath(libcuba._name)
    except OSError:
        raise OSError(
            f"Could not load {_libcuba_file} from system search paths or "
            f"the explicit path: {_libcuba_path_explicit}. "
            "Please set the 'LIBCUBA' environment variable "
            "to the correct path."
        )


# ========================================================================
# Global definitions
# ========================================================================

# Types
class _BOUNDS(Structure):
    _fields_ = ('lower', c_double), ('upper', c_double)


NULL: _Pointer = POINTER(c_int)()

# Prototypes: callable castings
_integrand_type: type[_CFuncPtr] = CFUNCTYPE(
    c_int,
    POINTER(c_int),
    POINTER(c_double),
    POINTER(c_int),
    POINTER(c_double),
    c_void_p,
)

_peakfinder_type: type[_CFuncPtr] = CFUNCTYPE(
    c_void_p,
    POINTER(c_int),
    POINTER(_BOUNDS),
    POINTER(c_int),
    POINTER(c_double),
)

# Constants
"""Cuda subroutine default parameters.

See Also
--------
`Cuba homepage <http://www.feynarts.de/cuba/>`_

"""
EPSREL: float = 1.e-3
EPSABS: float = 1.e-12
MINEVAL: int = 0
MAXEVAL: int = 50000
STATEFILE: _Pointer = NULL
SPIN: _Pointer = NULL

NSTART: int = 1000
NINCREASE: int = 500
NBATCH: int = 1000
GRIDNO: int = 0

NNEW: int = 1000
NMIN: int = 2
FLATNESS: float = 50.


# ========================================================================
# Wrappers
# ========================================================================

def _wrap_integrand(integrand: Callable) -> _CFuncPtr:
    use_raw_callback = isinstance(integrand, _CFuncPtr)
    return integrand if use_raw_callback else _integrand_type(integrand)


def Vegas(
    integrand: Callable,
    ndim: int,
    *,
    ncomp: int = 1,
    userdata: _Pointer = NULL,
    nvec: int = 1,
    epsrel: float = EPSREL,
    epsabs: float = EPSABS,
    verbose: int = 0,
    seed: int = None,
    mineval: int = MINEVAL,
    maxeval: int = MAXEVAL,
    nstart: int = NSTART,
    nincrease: int = NINCREASE,
    nbatch: int = NBATCH,
    gridno: int = GRIDNO,
    statefile: _Pointer = NULL,
) -> dict:
    """The Vegas subroutine."""
    neval = c_int()
    fail = c_int()
    comp = c_int()

    ARR = c_double * ncomp
    integral = ARR()
    error = ARR()
    prob = ARR()

    seed = seed or 0

    libcuba.Vegas(
        ndim, ncomp,
        _wrap_integrand(integrand), userdata, c_int(nvec),
        c_double(epsrel), c_double(epsabs),
        verbose,
        seed,
        mineval, maxeval,
        nstart, nincrease, nbatch,
        gridno,
        statefile, SPIN,
        byref(neval), byref(fail),
        integral, error, prob
    )

    return dict(
        neval=neval.value,
        fail=fail.value,
        comp=comp.value,
        results=[
            {
                'integral': integral[icomp],
                'error': error[icomp],
                'prob': prob[icomp],
            }
            for icomp in range(ncomp)
        ],
    )


def Suave(
    integrand: Callable,
    ndim: int,
    *,
    ncomp: int = 1,
    userdata: _Pointer = NULL,
    nvec: int = 1,
    epsrel: float = EPSREL,
    epsabs: float = EPSABS,
    verbose: int = 0,
    seed: int = None,
    mineval: int = MINEVAL,
    maxeval: int = MAXEVAL,
    nnew: int = NNEW,
    nmin: int = NMIN,
    flatness: float = FLATNESS,
    statefile: _Pointer = NULL,
) -> dict:
    """The Suave subroutine."""
    neval = c_int()
    fail = c_int()
    comp = c_int()
    nregions = c_int()

    ARR = c_double * ncomp
    integral = ARR()
    error = ARR()
    prob = ARR()

    seed = seed or 0

    libcuba.Suave(
        ndim, ncomp,
        _wrap_integrand(integrand), userdata, c_int(nvec),
        c_double(epsrel), c_double(epsabs),
        verbose,
        seed,
        mineval, maxeval,
        nnew, nmin,
        c_double(flatness),
        statefile, SPIN,
        byref(nregions), byref(neval), byref(fail),
        integral, error, prob
    )

    return dict(
        neval=neval.value,
        fail=fail.value,
        comp=comp.value,
        nregions=nregions.value,
        results=[
            {
                'integral': integral[icomp],
                'error': error[icomp],
                'prob': prob[icomp],
            }
            for icomp in range(ncomp)
        ],
    )


def Divonne(
    integrand: Callable,
    ndim: int,
    key1: int,
    key2: int,
    key3: int,
    maxpass: int,
    border: float,
    maxchisq: float,
    mindeviation: float,
    *,
    ncomp: int = 1,
    userdata: _Pointer = NULL,
    nvec: int = 1,
    epsrel: float = EPSREL,
    epsabs: float = EPSABS,
    verbose: int = 0,
    seed: int = None,
    mineval: int = MINEVAL,
    maxeval: int = MAXEVAL,
    ldxgiven: int = None,
    xgiven: list[float] = None,
    nextra: int = 0,
    peakfinder: Callable = None,
    statefile: _Pointer = NULL,
) -> dict:
    """The Divonne subroutine."""
    neval = c_int()
    fail = c_int()
    comp = c_int()
    nregions = c_int()

    ARR = c_double * ncomp
    integral = ARR()
    error = ARR()
    prob = ARR()

    seed = seed or 0

    if ldxgiven is None:
        ldxgiven = ndim

    if xgiven is None:
        ngiven = 0
        xgiven = NULL
    else:
        ngiven = len(xgiven)
        xgiven = ARR(xgiven)

    if peakfinder is None:
        peakfinder = NULL
    else:
        peakfinder = _peakfinder_type(peakfinder)

    libcuba.Divonne(
        ndim, ncomp,
        _wrap_integrand(integrand), userdata, c_int(nvec),
        c_double(epsrel), c_double(epsabs),
        verbose,
        seed,
        mineval, maxeval,
        key1, key2, key3,
        maxpass,
        c_double(border),
        c_double(maxchisq),
        c_double(mindeviation),
        ngiven, ldxgiven, xgiven,
        nextra,
        peakfinder,
        statefile, SPIN,
        byref(nregions), byref(neval), byref(fail),
        integral, error, prob
    )

    return dict(
        neval=neval.value,
        fail=fail.value,
        comp=comp.value,
        nregions=nregions.value,
        results=[
            {
                'integral': integral[icomp],
                'error': error[icomp],
                'prob': prob[icomp],
            }
            for icomp in range(ncomp)
        ],
    )


def Cuhre(
    integrand: Callable,
    ndim: int,
    *,
    ncomp: int = 1,
    userdata: _Pointer = NULL,
    nvec: int = 1,
    epsrel: float = EPSREL,
    epsabs: float = EPSABS,
    verbose: int = 0,
    # seed: int = None,
    mineval: int = MINEVAL,
    maxeval: int = MAXEVAL,
    key: int = 0,
    statefile: _Pointer = NULL,
) -> dict:
    """The Cuhre subroutine."""
    neval = c_int()
    fail = c_int()
    comp = c_int()
    nregions = c_int()

    ARR = c_double * ncomp
    integral = ARR()
    error = ARR()
    prob = ARR()

    # seed = seed or 0

    libcuba.Cuhre(
        ndim, ncomp,
        _wrap_integrand(integrand), userdata, c_int(nvec),
        c_double(epsrel), c_double(epsabs),
        verbose,
        mineval, maxeval,
        key,
        statefile, SPIN,
        byref(nregions), byref(neval), byref(fail),
        integral, error, prob
    )

    return dict(
        neval=neval.value,
        fail=fail.value,
        comp=comp.value,
        nregions=nregions.value,
        results=[
            {
                'integral': integral[icomp],
                'error': error[icomp],
                'prob': prob[icomp],
            }
            for icomp in range(ncomp)
        ],
    )


def demo():
    """PyCuba library demo."""

    # ---- Preamble ------------------------------------------------------

    import math

    def integrand_demo(ndim, xx, ncomp, ff, userdata):
        x, y, z = [xx[i] for i in range(ndim.contents.value)]
        ff[0] = math.sin(x) * math.cos(y) * math.exp(z)
        return 0

    def print_pkginfo():
        print("PyCubaX version:", __version__)
        print("LibCuba source:", _libcuba_source)
        print()

    def print_demo_header(name):
        print(f"---- {name} demo ----")
        print()

    def print_demo_results(name, results):
        KEYS = ['nregions', 'neval', 'fail',]

        print()

        attrs = [k for k in KEYS if k in results]
        attrs_str = ["{} {:d}".format(attr, results[attr]) for attr in attrs]
        print(f"{name} status:\t" + '\t'.join(attrs_str))

        for comp in results['results']:
            print(
                f"{name} result:\t" +
                "{integral:.5f} +- {error:.5e}\tp = {prob:.5f}\n"
                .format(**comp)
            )

    # ---- Parameters ----------------------------------------------------

    # Common parameters
    _NDIM = 3
    # _NCOMP = 1
    # _MINEVAL = MINEVAL
    # _MAXEVAL = MAXEVAL

    flag_verbose = int(os.getenv('CUBAVERBOSE', 2))
    flag_lastsamp = 4
    flag_all = flag_verbose | flag_lastsamp

    # Suave subroutine parameters
    # _NNEW = NNEW
    # _NMIN = NMIN
    # _FLATNESS = FLATNESS

    # Divonne subroutine parameters
    _KEY1 = 47
    _KEY2 = 1
    _KEY3 = 1
    _MAXPASS = 5
    _BORDER = 0.
    _MAXCHISQ = 10.
    _MINDEVIATION = .25
    _LDXGIVEN = _NDIM
    # _NEXTRA = 0

    # Cuhre subroutine parameters
    # _KEY = 0

    # ---- Runs ----------------------------------------------------------

    print_pkginfo()

    # Vegas demo
    print_demo_header('Vegas')
    vegas_results = Vegas(integrand_demo, _NDIM, verbose=flag_verbose)
    print_demo_results('Vegas', vegas_results)

    # Suave demo
    print_demo_header('Suave')
    suave_results = Suave(integrand_demo, _NDIM, verbose=flag_all)
    print_demo_results('Suave', suave_results)

    # Divonne demo
    print_demo_header('Divonne')
    divonne_results = Divonne(
        integrand_demo, _NDIM,
        key1=_KEY1, key2=_KEY2, key3=_KEY3,
        maxpass=_MAXPASS,
        border=_BORDER,
        maxchisq=_MAXCHISQ,
        mindeviation=_MINDEVIATION,
        ldxgiven=_LDXGIVEN,
        verbose=flag_verbose,
    )
    print_demo_results('Divonne', divonne_results)

    # Cuhre demo
    print_demo_header('Cuhre')
    cuhre_results = Cuhre(integrand_demo, _NDIM, verbose=flag_all)
    print_demo_results('Cuhre', cuhre_results)

    return 0


if __name__ == '__main__':
    demo()
