# Makefile for audio library
CC = gcc
CFLAGS = -Wall -Wextra -O3 -fPIC -std=c99
LDFLAGS = -shared -Wl,--export-dynamic
LIBS = -lportaudio -lsndfile -lsamplerate -lpthread -lm

# Detect OS for library naming
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
    LIBNAME = libaudio.dylib
    CFLAGS += -I/usr/local/include -I/opt/homebrew/include
    LDFLAGS = -shared -undefined dynamic_lookup
    LDFLAGS += -L/usr/local/lib -L/opt/homebrew/lib
else ifeq ($(UNAME_S),Linux)
    LIBNAME = libaudio.so
else
    LIBNAME = libaudio.dll
    LIBS += -lole32 -lwinmm
    LDFLAGS = -shared
endif

SOURCES = $(wildcard *.c)
OBJECTS = $(SOURCES:.c=.o)

.PHONY: all clean install

all: $(LIBNAME)

$(LIBNAME): $(OBJECTS)
	$(CC) $(LDFLAGS) -o $@ $^ $(LIBS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJECTS) $(LIBNAME)

install: $(LIBNAME)
	sudo cp $(LIBNAME) /usr/local/lib/
	sudo ldconfig 2>/dev/null || true

# Development target with debug symbols
debug: CFLAGS += -g -DDEBUG
debug: $(LIBNAME)

# Check dependencies
check-deps:
	@echo "Checking dependencies..."
	@pkg-config --exists portaudio-2.0 || (echo "PortAudio not found!" && false)
	@pkg-config --exists sndfile || (echo "libsndfile not found!" && false)
	@echo "All dependencies found!"
