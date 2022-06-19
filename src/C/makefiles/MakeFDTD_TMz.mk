###############################################################################
#	TMz FDTD Demo Makefile			         						          #
#																	          #
#	Project:	PyCEM        										          #
#	Date:		01/18/2022											          #
#																	          #
###############################################################################

## Library and executable filename
LIBFILE = libFDTD_TMz.so
BINFILE = FDTD_TMz

## Compiler
CC=gcc					# GNU C Compiler

## Directories
SRCDIR = ../src/fdtd_tmz
OBJDIR = ../src/fdtd_tmz/obj
INCDIR = ../inc
BINDIR = ../bin
LIBDIR = ../lib

## Compiler flags
CFLAGS := -I$(INCDIR)	# Look in inc directory for header files
CFLAGS += -fPIC			# Generate position independent code (for shared lib)
CFLAGS += -Wall			# Enables warnings for all questionable constructions
CFLAGS += -Wextra		# Enables additional warnings
CFLAGS += -Wconversion	# Warn for implicit conversions that may alter a value
CFLAGS += -Werror		# Make all warnings into errors
CFLAGS += -g			# GCC compiler core dump: "ulimit -c unlimited" if fail
CFLAGS += -O3			# Enable many optimizations

CFLAGS_EXEC := $(filter-out -fPIC -O3, $(CFLAGS))

## Define libraries
LIBS = -lpthread		# Necessary when including pthread.h
LIBS += -lm				# Math library, only necessary if including math.h

## Define source, dependencies (headers), and object files
SRC = $(wildcard $(SRCDIR)/*.c)

DEPS = $(INCDIR)/fdtd_tmz.h

OBJ := $(addprefix $(OBJDIR)/, $(notdir $(SRC)))
OBJ := $(OBJ:.c=.o)

OBJ_EXEC = $(OBJ:.o=.x.o)

## Ensure make executes all rules for shared library
all: $(LIBDIR)/$(LIBFILE)

## Create objects for library
.SECONDEXPANSION:
$(OBJ): $$(addprefix $(SRCDIR)/, $$(patsubst %.o,%.c,$$(@F))) $(DEPS)
	$(CC) -c $< $(CFLAGS) -o $@ $(LIBS)

## Create shared library
$(LIBDIR)/$(LIBFILE): $(OBJ)
	$(CC) -shared -o $@ $(OBJ)

## Create objects for executable
.SECONDEXPANSION:
$(OBJ_EXEC): $$(addprefix $(SRCDIR)/, $$(patsubst %.x.o,%.c,$$(@F))) $(DEPS)
	$(CC) -c $< $(CFLAGS_EXEC) -o $@ $(LIBS)

## Create executable file (for debugging)
$(BINDIR)/$(BINFILE): $(OBJ_EXEC)
	$(CC) -o $@ $(OBJ_EXEC) $(LIBS)

## Indicate phony targets
.PHONY: clean all 		# Runs rules even if files named "clean" or "all" exist

## Clean up
clean:
	rm -f $(OBJDIR)/*.o *~ core $(INCDIR)/*~ $(LIBDIR)/$(LIBFILE) $(BINDIR)/*

## Make executable for debugging purposes
exec: $(BINDIR)/$(BINFILE)