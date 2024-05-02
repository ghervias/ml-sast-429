TARGET=juliet-example

# Bins
MAKE=make
CC=wllvm
CFLAGS=-g
LFLAGS=-lpthread

SRC_DIR=src/
SUP_DIR=support/
INCLUDE=inc/

SRCS=$(wildcard $(SRC_DIR)*.c)
OBJS=$(patsubst %.c,%.o,$(SRCS))

SUP_SRCS=$(wildcard $(SUP_DIR)*.c)
SUP_OBJS=$(patsubst %.c,%.o,$(SUP_SRCS))

MAIN=main.c

$(TARGET): $(OBJS) $(SUP_OBJS)
	$(CC) $(CFLAGS) $(LFLAGS) -I $(INCLUDE) $^ -o $@ $(MAIN)

%.o: %.c
	$(CC) $(CFLAGS) -I $(INCLUDE) -o $@ -c $<


.PHONY: clean

clean:
	rm -f juliet-example */.*.o.bc .*.o.bc */*.o *.o 
