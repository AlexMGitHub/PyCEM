###############################################################################
#	Benchmarking Makefile			         						          #
#																	          #
#	Project:	PyCEM        										          #
#	Date:		12/11/2021											          #
#																	          #
###############################################################################

## Library filename
LIBFILE = libbenchmarking.so

## Compiler
CC=gcc					# GNU C Compiler

## Directories
SRCDIR = ./src
OBJDIR = ./src/obj
INCDIR = ./inc
BINDIR = ./bin
LIBDIR = ./lib

## Compiler flags
CFLAGS = -I$(INCDIR)	# Look in inc directory for header files
CFLAGS += -fpic			# Generate position independent code (for shared lib)
CFLAGS += -Wall			# Enables warnings for all questionable constructions
CFLAGS += -Wextra		# Enables additional warnings
CFLAGS += -Wconversion	# Warn for implicit conversions that may alter a value
CFLAGS += -Werror		# Make all warnings into errors
CFLAGS += -g			# GCC compiler core dump: "ulimit -c unlimited" if fail
CFLAGS += -O3			# Enable many optimizations

## Define libraries
LIBS = -lpthread		# Necessary when including pthread.h
# LIBS += -lm			# Math library, only necessary if including math.h

## Define source, dependencies (headers), and object files
## Then append directory to the filenames
_SRC = benchmarking.c
SRC = $(_SRC:%=$(SRCDIR)/%)

_DEPS = benchmarking.h
DEPS = $(_DEPS:%=$(INCDIR)/%)

_OBJ = $(_SRC:.c=.o)
OBJ = $(_OBJ:%=$(OBJDIR)/%)

## Ensure make executes all rules
all: $(LIBDIR)/$(LIBFILE)

## Create objects
$(OBJDIR)/%.o: $(SRCDIR)/%.c $(DEPS)
	$(CC) -c $< $(CFLAGS) -o $(OBJ) $(LIBS)

## Create shared library
$(LIBDIR)/$(LIBFILE): $(OBJ)
	$(CC) -shared -o $@ $(OBJ)

## Indicate phony targets
.PHONY: clean all 		# Runs rules even if files named "clean" or "all" exist

## Clean up
clean:
	rm -f $(OBJDIR)/*.o *~ core $(INCDIR)/*~ $(LIBDIR)/$(LIBFILE)