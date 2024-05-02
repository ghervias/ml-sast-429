#!/bin/bash

export LLVM_COMPILER=clang
export CC=wllvm
export CXX=wllvm++

# Needs generation of header file(s).
cd miniupnpc && make miniupnpcstrings.h && cd .. \
&& wllvm -O0 -g \
    -DUSE_MINIUPNP \
    -D_GNU_SOURCE \
    -I./miniupnpc \
    -static \
    ./miniupnpc/connecthostport.c \
    ./miniupnpc/igd_desc_parse.c \
    ./miniupnpc/minisoap.c \
    ./miniupnpc/minissdpc.c \
    ./miniupnpc/miniupnpc.c \
    ./miniupnpc/miniwget.c \
    ./miniupnpc/portlistingparse.c \
    ./miniupnpc/receivedata.c \
    ./miniupnpc/upnpcommands.c \
    ./miniupnpc/upnperrors.c \
    ./miniupnpc/upnpreplyparse.c \
    ./miniupnpd/minixml.c \
    -o entrypoint ../entrypoints.c
