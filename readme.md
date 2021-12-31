# CEM

## Overview


### Motivation for writing C Extensions
The Python interpreter can be extended with new modules written in the C programming language.  This means that functions written in C and compiled as a shared library can be called in Python code as if they were written natively in Python.

Python has two major performance limitations: one, it is an interpreted language and as such will always be slower than a compiled language.  Two, Python has the so-called "Global Interpreter Lock" (GIL) which prevents truly parallel multi-threading.  Python's `threading` module is limited to concurrent multi-threading, meaning that only one thread can execute Python code at once because each thread must acquire the GIL before executing code.  Parallel computation can be achieved by using the `multiprocessing` library, but subprocesses have more overhead than threads and do not benefit from shared memory.

Both of these performance limitations can be bypassed by writing C extensions.  C is a compiled language, and is well-known to be highly optimized and fast to execute.  In addition, by using a C extension the GIL can be bypassed to allow for true parallel multi-threading.  The CEM solver will be performing many matrix operations which are CPU-intensive and can benefit from parallelism.  Writing C extensions to execute these matrix operations will significantly improve the performance of the solver.

### Doxygen

### CEM Codes

#### MOM
#### FEM
#### FDTD

## References

* C
http://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html
http://websites.umich.edu/~eecs381/handouts/CHeaderFileGuidelines.pdf
https://people.engr.tamu.edu/j-welch/teaching/cstyle.html


* Python
https://numpy.org/doc/stable/reference/arrays.scalars.html#numpy.int_

* C Extension
https://stackoverflow.com/questions/43148188/python-2d-array-i-c-using-ctypes
https://docs.python.org/3/library/ctypes.html
https://www.cprogramming.com/tutorial/shared-libraries-linux-gcc.html
https://medium.com/meatandmachines/shared-dynamic-libraries-in-the-c-programming-language-8c2c03311756
https://github.com/realpython/materials
https://realpython.com/python-bindings-overview/#ctypes
https://realpython.com/build-python-c-extension-module/#extending-your-python-program
https://dbader.org/blog/python-ctypes-tutorial

* Matrices
https://cse.buffalo.edu/faculty/miller/Courses/CSE633/Ortega-Fall-2012-CSE633.pdf
https://cse.buffalo.edu/faculty/miller/Courses/CSE702/Prithvisagar-Rao-Fall-2020.pdf
