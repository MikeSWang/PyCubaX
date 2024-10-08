#!/usr/bin/env bash
# @file make_sharedlib.sh
# @brief A script for creating shared library ``libcuba.so``.
# @author Johannes Buchner (C) 2015
# @author Mike S Wang (C) 2024

# Preamble
function bfecho {
    echo -e "\033[1m$@\033[0m"
}

LIBNAME=libcuba
if [[ $(uname -s) == 'Darwin' ]]; then
    LIBSUFFIX=.dylib
elif [[ $(uname -s) == 'Linux' ]]; then
    LIBSUFFIX=.so
else
    echo "Unsupported operating system: $(uname -s)"
    exit 1
fi

DISTDIR=dist

CC=${CC:-gcc}

# Patch the source code.
bfecho "Patching up source code..."
patch -p1 < $(find patches -type f -name "*.patch")
echo

# Export environment variables.
bfecho "Exporting environment variables..."
CFLAGS_LIST=(-fPIC -fomit-frame-pointer -Ofast -Wall)
if [[ $(uname -s) == 'Darwin' ]]; then
    CFLAGS_LIST+=(-mmacos-version-min=11.0 -mcpu=apple-m1 -mtune=native)
else
    CFLAGS_LIST+=(-march=native)
fi
echo "export CFLAGS=\${CFLAGS:-${CFLAGS_LIST[@]}}"
export CFLAGS=${CFLAGS:-${CFLAGS_LIST[@]}}
echo

# Configure
bfecho "Configuring..."
./configure
echo

# Build default static library.
bfecho "Rebuilding static library..."
make -B ${LIBNAME}.a
echo

# Build shared library from unpacked static library.
bfecho "Unpacking static library..."
OBJFILES=$(ar xv libcuba.a | sed 's|x - ||g' | grep -v '__.SYMDEF SORTED')
echo

bfecho "Building shared library..."
${CC} -shared -Wall ${OBJFILES} -o ${LIBNAME}${LIBSUFFIX} -lm
echo

# Move libraries to dist directory.
bfecho "Moving libraries to dist directory..."
mkdir -p "${DISTDIR}"
find . -maxdepth 1 -type f -name "${LIBNAME}.*" -exec mv {} "${DISTDIR}" \;
echo

# Clean up.
bfecho "Cleaning up..."

echo "... unpatching source code"
patch -R -p1 < $(find patches -type f -name "*.patch")
echo

echo "... deleting auxiliary files"
find . -type f -name "*.rej" -o -name "*.orig" -exec rm {} \;
rm config.h config.log config.status makefile '__.SYMDEF SORTED' ${OBJFILES}
echo
