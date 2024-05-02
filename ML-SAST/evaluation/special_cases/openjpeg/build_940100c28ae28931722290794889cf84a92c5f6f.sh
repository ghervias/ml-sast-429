#!/bin/bash

export LLVM_COMPILER=clang
export CC=wllvm
export CXX=wllvm++

BUILD_DIR=build

# Needs to run cmake because wllvm uses generated source files
cmake --no-warn-unused-cli \
    -DCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=TRUE \
    -DCMAKE_BUILD_TYPE:STRING=Debug \
    -DCMAKE_C_COMPILER:FILEPATH=/root/node_modules/llvm-13.0.0.obj/bin/clang \
    -DCMAKE_CXX_COMPILER:FILEPATH=/root/node_modules/llvm-13.0.0.obj/bin/clang++ \
    -S. \
    -B$BUILD_DIR \
&& cmake --build $BUILD_DIR \
&& wllvm -O0 -g \
    -DUSE_OPENJPEG \
    -I./src/lib/openjp2 -I./build/src/lib/openjp2 \
    -static \
    ./src/lib/openjp2/bio.c \
    ./src/lib/openjp2/cio.c \
    ./src/lib/openjp2/dwt.c \
    ./src/lib/openjp2/event.c \
    ./src/lib/openjp2/function_list.c \
    ./src/lib/openjp2/image.c \
    ./src/lib/openjp2/invert.c \
    ./src/lib/openjp2/j2k.c \
    ./src/lib/openjp2/jp2.c \
    ./src/lib/openjp2/mct.c \
    ./src/lib/openjp2/mqc.c \
    ./src/lib/openjp2/openjpeg.c \
    ./src/lib/openjp2/pi.c \
    ./src/lib/openjp2/raw.c \
    ./src/lib/openjp2/t1.c \
    ./src/lib/openjp2/t2.c \
    ./src/lib/openjp2/tcd.c \
    ./src/lib/openjp2/tgt.c \
    -lm \
    -o entrypoint ../entrypoints.c

