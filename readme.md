# PyCEM

<p align="center">
<img src="docs/img/pycem.gif" title="The Whole Enchilada" alt="The Whole Enchilada" width="600"/>
</p>

## Overview

PyCEM is a computational electromagnetics (CEM) learning project that visualizes electromagnetic simulations using PyVista and a Dash web app.

The purpose of this learning project is threefold:

1. Learn more about the three major CEM techniques: FDTD, MoM, and FEM.
2. Learn how to use PyVista and Dash to build and visualize meshes for these CEM techniques.
3. Improve my proficiency in writing C code, and integrate my C shared libraries with Python code to enable fast parallel multithreading in a Python web application.

PyCEM is currently a work in progress.  To date, I have a functional Dash web app that allows the user to browse a collection of two-dimensional FDTD scenarios.  The user can run the simulations with a click of a button, and then view the resulting PyVista animations in the browser.  The simulations are defined as Python classes, and NumPy arrays are passed to the C code as a `struct` of pointers.  Once the simulation is complete, the NumPy array containing the E-field values at each time step is represented as a PyVista mesh and used to generate an animation of the E-fields changing over time.

I plan to write a three-dimensional FDTD solver next, and explore the possibility of creating ports that I can extract S-parameters and characteristic impedances from.  It would also be of interest to calculate far field radiation patterns for antenna simulations.

The long-term goal is to create similar solvers for both Method of Moments (MoM) and Finite Element Method (FEM) codes.

## Running the Docker container

PyCEM can be run by building a Docker image and spinning up a container using the following command in the PyCEM directory:

```bash
docker compose up -d
```

The above command will run PyCEM in production mode.  If you'd like to run PyCEM in development mode use the following command:

```bash
docker compose -f docker-compose.yml -f docker/docker-compose.dev.yml up -d
```

docker compose -f docker/docker-compose.dev.yml up

docker compose up

Used Ubuntu image because needed GLIBC version 2.34; Python 3.7 image had 2.31

## Motivation for writing a C Library

Python has two major performance limitations: one, it is an interpreted language and as such will always be slower than a compiled language.  Two, Python has the so-called "Global Interpreter Lock" (GIL) which prevents truly parallel multithreading.  Python's `threading` module is limited to concurrent multithreading, meaning that only one thread can execute Python code at once because each thread must acquire the GIL before executing code.  Parallel computation can be achieved by using the `multiprocessing` library, but subprocesses have more overhead than threads and do not benefit from shared memory.

Both of these performance limitations can be bypassed by writing C code.  C is a compiled language, and is well-known to be highly optimized and fast to execute.  In addition, by using an external C library the GIL can be bypassed to allow for true parallel multithreading.  The CEM solver will be running many CPU-intensive routines and can benefit from parallelism.  Writing C code to execute these routines will significantly improve the performance of the solver.

Functions written in C and compiled as a shared library can be called in Python code as if they were written natively in Python.  One method of doing so is to use the `ctypes` foreign function library.

## Visualizing Simulations

These CEM simulations should result in compelling visualizations.  I wanted a GUI front-end that would allow the user to run the simulation and view the field results.  I initially investigated [Kivy](https://kivy.org/) as a cross-platform framework for this purpose.  But after spending dozens of hours creating a prototype Kivy GUI that could play animations, I discovered PyVista.

### PyVista

[PyVista](https://www.pyvista.org/) is a Python wrapper of the Visualization Toolkit (VTK).  It makes 3D visualization and mesh analysis for scientific and engineering applications possible in Python.  This is exactly the type of visualization tool that grid or mesh-based CEM solvers require!  And, it allows the export of animations as GIF or MP4 files.

### Dash

PyVista also allows the user to rotate, zoom, and otherwise manipulate the plotted mesh - but only in a Jupyter notebook.  Interestingly, [Plotly's Dash](https://plotly.com/dash/) includes [Dash VTK](https://dash.plotly.com/vtk) for pushing VTK visualizations to the client's browser.  This allows for all of the interactive functionality that would normally only be available in a Jupyter notebook.  In addition to that, Dash web apps are quick to create and come with built-in components for user interaction and displaying plots.  It also has [Bootstrap components](https://dash-bootstrap-components.opensource.faculty.ai/) for quickly producing visually-appealing layouts.  On top of all of that, every operating system can run a browser - which makes cross-compatibility moot.  Once I realized all of this I tossed my Kivy code in the garbage and started over with Dash and PyVista.

## CEM Codes

### FDTD

Finite Difference Time Domain (FDTD) is considered the easiest CEM code to get started with.  I heavily relied on Professor John B. Schneider's e-book [Understanding the FDTD Method](https://eecs.wsu.edu/~schneidj/ufdtd/).  I used his [source code](https://github.com/john-b-schneider/uFDTD) as a starting point for my FDTD solver, which is permitted per the Creative Commons Attribution-ShareAlike 4.0 International license.

### MoM

WIP.

### FEM

WIP.

## References

* Icons
  * <https://feathericons.com/?query=play>

* C
  * <http://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html>
  * <http://websites.umich.edu/~eecs381/handouts/CHeaderFileGuidelines.pdf>
  * <https://people.engr.tamu.edu/j-welch/teaching/cstyle.html>
  * <https://stackoverflow.com/questions/63220508/how-can-i-define-a-pointer-to-variable-length-array-vla-in-a-struct-or-equiva>
  * <https://stackoverflow.com/questions/14808908/pointer-to-2d-arrays-in-c>
  * <https://stackoverflow.com/questions/36890624/malloc-a-2d-array-in-c>

* Python
  * <https://numpy.org/doc/stable/reference/arrays.scalars.html#numpy.int_>
  * <https://stackoverflow.com/questions/57025836/how-to-check-if-a-given-number-is-a-power-of-two>

* C Extension
  * <https://stackoverflow.com/questions/43148188/python-2d-array-i-c-using-ctypes>
  * <https://docs.python.org/3/library/ctypes.html>
  * <https://www.cprogramming.com/tutorial/shared-libraries-linux-gcc.html>
  * <https://medium.com/meatandmachines/shared-dynamic-libraries-in-the-c-programming-language-8c2c03311756>
  * <https://github.com/realpython/materials>
  * <https://realpython.com/python-bindings-overview/#ctypes>
  * <https://realpython.com/build-python-c-extension-module/#extending-your-python-program>
  * <https://dbader.org/blog/python-ctypes-tutorial>

* Matrices
  * <https://cse.buffalo.edu/faculty/miller/Courses/CSE633/Ortega-Fall-2012-CSE633.pdf>
  * <https://cse.buffalo.edu/faculty/miller/Courses/CSE702/Prithvisagar-Rao-Fall-2020.pdf>

* FDTD
  * <https://eecs.wsu.edu/~schneidj/ufdtd/>
  * <https://github.com/john-b-schneider/uFDTD>

* Docker build issues
  * <https://stackoverflow.com/questions/54633657/how-to-install-pip-for-python-3-7-on-ubuntu-18>
  * <https://github.com/pypa/get-pip/issues/124>
  * <https://itsmycode.com/importerror-libgl-so-1-cannot-open-shared-object-file-no-such-file-or-directory/>
