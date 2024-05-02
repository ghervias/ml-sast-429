#!/bin/bash

export LLVM_COMPILER=clang
export CC=wllvm
export CXX=wllvm++

wllvm -O0 -g \
    -DUSE_ZLIB \
    -static \
    adler32.c \
    compress.c \
    crc32.c \
    deflate.c \
    gzclose.c \
    gzlib.c \
    gzread.c \
    gzwrite.c \
    infback.c \
    inffast.c \
    inflate.c \
    inftrees.c \
    trees.c \
    uncompr.c \
    zutil.c \
    -o entrypoint ../entrypoints.c

