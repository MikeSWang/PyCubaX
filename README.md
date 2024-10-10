# PyCuba(X): a new Python wrapper for the Cuba library

[![Release](https://img.shields.io/github/v/release/MikeSWang/PyCubaX?display_name=tag&sort=semver&logo=Git)](https://github.com/MikeSWang/PyCubaX/releases/latest)
[![CI](https://img.shields.io/github/actions/workflow/status/MikeSWang/PyCubaX/ci.yml?label=ci&logo=GitHubActions)](https://github.com/MikeSWang/PyCubaX/actions/workflows/ci.yml)

The PyCuba(X) package provides a Python wrapper for the Cuba library, which
offers a choice of four independent routines for multidimensional
numerical integration: Vegas, Suave, Divonne, and Cuhre.

## Installation

### Cuba library

In the cloned repository, execute in shell

```sh
./make_sharedlib.sh
```

This creates ``libcuba.[a,so,dylib]`` inside the ``dist/`` folder.

### PyCuba(X) package

Provided `pip` is available as part of your Python environment, run

```sh
python -m pip install --editable . -vvv
```

to install in local editable mode.

> [!NOTE]
> This automatically creates the shared library in the ``dist/`` folder.
> If the library remains there or is in system search paths, it should be
> automatically discoverable; if for any reason it is moved to a
> non-standard location, set the environmental variable `LIBCUBA` to
> its path before importing ``pycuba``.

## Usage

Simply import the desired integration routine, e.g.

```py
from pycuba import Vegas
```

As a demo, run

```py
from pycuba import demo; demo()
```

See PyCuba
[documentation](https://johannesbuchner.github.io/PyMultiNest/pycuba.html)
and [repository](https://github.com/JohannesBuchner/PyMultiNest) for
more details.

> [!TIP]
> If you encounter an error about loading the Cuba library, see the note above
> regarding the discoverability of ``libcuba``.

## Acknowledgement

The ``Cuba`` library is written by
[Thomas Hahn](https://wwwth.mpp.mpg.de/members/hahn/)
and is available at <http://www.feynarts.de/cuba/>
under the LGPLv3 licence.

The ``PyCuba`` package is written by
[Johannes Buchner](https://github.com/JohannesBuchner)
and is available as part of
[``PyMultiNest``](https://github.com/JohannesBuchner/PyMultiNest)
under the GPLv3 licence.

Both libraries/packages have been modified and redistributed here under
the GLPv3+ licence. Changes are detailed in [`CHANGELOG.md`](./CHANGELOG.md).

## Licence

[![Licence](https://img.shields.io/github/license/MikeSWang/PyCubaX?label=licence&style=flat-square&color=informational)](https://github.com/MikeSWang/PyCubaX/blob/main/LICENCE)

``PyCubaX`` is made freely available under the
[GPLv3+ licence](https://www.gnu.org/licenses/gpl-3.0.en.html).
Please see [``LICENCE``](./LICENCE) for full terms and conditions.

&copy; 2022 Thomas Hahn

&copy; 2016 Johannes Buchner

&copy; 2024 Mike S Wang
