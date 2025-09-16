#!/bin/bash
set -e

echo "Cross-compiling audio library for Windows..."

# Configuration
MINGW_PREFIX="x86_64-w64-mingw32"
CC="${MINGW_PREFIX}-gcc"
WIN_DEPS="win-libs"

# Check if cross-compiler is available
if ! command -v $CC &> /dev/null; then
    echo "Error: MinGW-w64 cross-compiler not found!"
    echo "Install it with: sudo apt-get install mingw-w64"
    exit 1
fi

# Check if Windows dependencies exist
if [ ! -d "$WIN_DEPS" ]; then
    echo "Warning: Windows dependencies not found in $WIN_DEPS"
    echo "You may need to build or download Windows versions of:"
    echo "  - PortAudio"
    echo "  - libsndfile"
    echo "  - libsamplerate"
fi

# Build command
CFLAGS="-O2 -Wall -Wextra"
LDFLAGS="-shared -Wl,--out-implib,libaudio.lib"
LIBS="-lportaudio -lsndfile -lsamplerate -lwinmm -lole32 -luuid -lksuser -lsetupapi"

if [ -d "$WIN_DEPS" ]; then
    CFLAGS="$CFLAGS -I${WIN_DEPS}/include"
    LDFLAGS="$LDFLAGS -L${WIN_DEPS}/lib"
fi

echo "Compiling with: $CC"
$CC $CFLAGS $LDFLAGS audio.c -o libaudio.dll $LIBS

if [ $? -eq 0 ]; then
    echo "Successfully built libaudio.dll"
    echo "Import library: libaudio.lib"

    # Check if we can get file info
    if command -v file &> /dev/null; then
        file libaudio.dll
    fi

    # List exported functions
    if command -v ${MINGW_PREFIX}-objdump &> /dev/null; then
        echo "Exported functions:"
        ${MINGW_PREFIX}-objdump -p libaudio.dll | grep "\\[.*\\]" | head -20
    fi
else
    echo "Build failed!"
    exit 1
fi
