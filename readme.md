# CEM

## Overview

### Motivation for writing C Library

Python has two major performance limitations: one, it is an interpreted language and as such will always be slower than a compiled language.  Two, Python has the so-called "Global Interpreter Lock" (GIL) which prevents truly parallel multithreading.  Python's `threading` module is limited to concurrent multithreading, meaning that only one thread can execute Python code at once because each thread must acquire the GIL before executing code.  Parallel computation can be achieved by using the `multiprocessing` library, but subprocesses have more overhead than threads and do not benefit from shared memory.

Both of these performance limitations can be bypassed by writing C code.  C is a compiled language, and is well-known to be highly optimized and fast to execute.  In addition, by using an external C library the GIL can be bypassed to allow for true parallel multithreading.  The CEM solver will be running many CPU-intensive routines and can benefit from parallelism.  Writing C code to execute these routines will significantly improve the performance of the solver.

Functions written in C and compiled as a shared library can be called in Python code as if they were written natively in Python.  One method of doing so is to use the `ctypes` foreign function library.

## Visualizing Simulations

These CEM simulations should result in compelling visualizations.  I wanted a GUI front-end that would allow the user to run the simulation and view the field results.  I initially investigated [Kivy](https://kivy.org/) as a cross-platform framework for this purpose.  But after spending dozens of hours creating a prototype Kivy GUI that could play animations, I discovered PyVista.

### PyVista

[PyVista](https://www.pyvista.org/) is a Python wrapper of the Visualization Toolkit (VTK).  It makes 3D visualization and mesh analysis for scientific and engineering applications possible in Python.  This is exactly the type of visualization tool that grid or mesh-based CEM solvers require!  And, it allows the export of animations as GIF or MP4 files.

### Dash

PyVista also allows the user to rotate, zoom, and otherwise manipulate the plotted mesh - but only in a Jupyter notebook.  Interestingly, [Plotly's Dash](https://plotly.com/dash/) includes [Dash VTK](https://dash.plotly.com/vtk) for pushing VTK visualizations to the client's browser.  This allows for all of the interactive functionality that would normally only be available in a Jupyter notebook.  In addition to that, Dash web apps are quick to create and come with built-in components for user interaction and displaying plots.  It also has [Bootstrap components](https://dash-bootstrap-components.opensource.faculty.ai/) for quickly producing visually-appealing layouts.  On top of all of that, every operating system can run a browser - which makes cross-compatibility moot.  Once I realized all of this I tossed my Kivy code in the garbage and started over with Dash and PyVista.

## Kivy

### Doxygen

### CEM Codes

#### MOM

#### FEM

#### FDTD

## References

* Icons
<https://feathericons.com/?query=play>

* C
<http://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html>
<http://websites.umich.edu/~eecs381/handouts/CHeaderFileGuidelines.pdf>
<https://people.engr.tamu.edu/j-welch/teaching/cstyle.html>
<https://stackoverflow.com/questions/63220508/how-can-i-define-a-pointer-to-variable-length-array-vla-in-a-struct-or-equiva>
<https://stackoverflow.com/questions/14808908/pointer-to-2d-arrays-in-c>
<https://stackoverflow.com/questions/36890624/malloc-a-2d-array-in-c>

* Python
<https://numpy.org/doc/stable/reference/arrays.scalars.html#numpy.int_>
<https://stackoverflow.com/questions/57025836/how-to-check-if-a-given-number-is-a-power-of-two>

* C Extension
<https://stackoverflow.com/questions/43148188/python-2d-array-i-c-using-ctypes>
<https://docs.python.org/3/library/ctypes.html>
<https://www.cprogramming.com/tutorial/shared-libraries-linux-gcc.html>
<https://medium.com/meatandmachines/shared-dynamic-libraries-in-the-c-programming-language-8c2c03311756>
<https://github.com/realpython/materials>
<https://realpython.com/python-bindings-overview/#ctypes>
<https://realpython.com/build-python-c-extension-module/#extending-your-python-program>
<https://dbader.org/blog/python-ctypes-tutorial>

* Matrices
<https://cse.buffalo.edu/faculty/miller/Courses/CSE633/Ortega-Fall-2012-CSE633.pdf>
<https://cse.buffalo.edu/faculty/miller/Courses/CSE702/Prithvisagar-Rao-Fall-2020.pdf>

* FDTD
<https://eecs.wsu.edu/~schneidj/ufdtd/>
<https://github.com/john-b-schneider/uFDTD>

* KIVY
<https://stackoverflow.com/questions/27643628/kivy-interpolation-on-canvas>
<https://stackoverflow.com/questions/41317215/how-do-i-move-a-kivy-widgets-canvas-items-if-the-items-are-defined-in-py-and-n>
<https://old.reddit.com/r/kivy/comments/ryfue4/kivy_graphics_cant_handle_thousands_of_rectangles/>
<https://kivy.org/doc/stable/api-kivy.graphics.texture.html>
<https://stackoverflow.com/questions/31254796/kivy-check-if-a-function-is-already-scheduled>
