#!/bin/bash

# Cross-compilation script for Windows
# Usage: ./build_windows.sh

# Set cross-compiler
export CC=x86_64-w64-mingw32-gcc
export CXX=x86_64-w64-mingw32-g++
export AR=x86_64-w64-mingw32-ar
export STRIP=x86_64-w64-mingw32-strip

# Paths to Windows dependencies
WIN_DEPS_DIR="win-libs"
INCLUDE_DIR="$WIN_DEPS_DIR/include"
LIB_DIR="$WIN_DEPS_DIR/lib"

# Compiler flags
CFLAGS="-O2 -Wall -I$INCLUDE_DIR -DWIN32 -D_WIN32_WINNT=0x0600"
LDFLAGS="-L$LIB_DIR -static-libgcc"
LIBS="-lportaudio -lsndfile -lsamplerate -lwinmm -lole32 -ldsound"

# Source files
SOURCES="audio.c"
OUTPUT="libaudio.dll"

echo "Cross-compiling for Windows..."
echo "CC: $CC"
echo "Includes: $INCLUDE_DIR"
echo "Libraries: $LIB_DIR"

# Compile shared library
$CC $CFLAGS -shared -o $OUTPUT $SOURCES $LDFLAGS $LIBS

if [ $? -eq 0 ]; then
    echo "✅ Successfully built $OUTPUT"
    echo "Size: $(ls -lh $OUTPUT | awk '{print $5}')"

    # Strip symbols to reduce size
    $STRIP $OUTPUT
    echo "Stripped size: $(ls -lh $OUTPUT | awk '{print $5}')"
else
    echo "❌ Build failed"
    exit 1
fi

# Optional: Create import library
echo "Creating import library..."
$AR rcs lib$(basename $OUTPUT .dll).a $OUTPUT
