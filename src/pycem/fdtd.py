"""Contains classes and functions used by the FDTD simulation."""
# %% Imports
# Standard system imports
import ctypes

# Related third party imports
import numpy as np

# Local application/library specific imports


# %% Classes
class ArrayStorage:
    """Stores references to array memory locations."""

    def __init__(self, Hx, Chxh, Chxe, Hy, Chyh, Chye, Ez, Ceze, Cezh):
        self.Hx = Hx
        self.Chxh = Chxh
        self.Chxe = Chxe
        self.Hy = Hy
        self.Chyh = Chyh
        self.Chye = Chye
        self.Ez = Ez
        self.Ceze = Ceze
        self.Cezh = Cezh


class Grid(ctypes.Structure):
    """Creates a class representing struct Grid."""

    _fields_ = [('Hx', ctypes.POINTER(ctypes.c_double)),
                ('Chxh', ctypes.POINTER(ctypes.c_double)),
                ('Chxe', ctypes.POINTER(ctypes.c_double)),
                ('Hy', ctypes.POINTER(ctypes.c_double)),
                ('Chyh', ctypes.POINTER(ctypes.c_double)),
                ('Chye', ctypes.POINTER(ctypes.c_double)),
                ('Ez', ctypes.POINTER(ctypes.c_double)),
                ('Ceze', ctypes.POINTER(ctypes.c_double)),
                ('Cezh', ctypes.POINTER(ctypes.c_double)),
                ('sizeX', ctypes.c_int),
                ('sizeY', ctypes.c_int),
                ('time', ctypes.c_int),
                ('max_time', ctypes.c_int),
                ('Cdtds', ctypes.c_double)]


# %% Functions
def grid_init(g, sizex, sizey, max_time):
    """Initialize pointer to struct Grid.

    Return reference to array memory locations.
    """
    imp0 = 377.0                    # Impedance of free space
    g.sizeX = sizex                 # X size of domain
    g.sizeY = sizey                 # Y size of domain
    g.time = 0                      # Current time step
    g.max_time = max_time           # Duration of simulation
    g.Cdtds = 1.0 / np.sqrt(2.0)    # Courant number

    # Initialize Numpy arrays
    Hx = np.zeros((g.sizeX, g.sizeY-1), dtype=np.double)
    Chxh = np.ones((g.sizeX, g.sizeY-1), dtype=np.double)
    Chxe = np.ones((g.sizeX, g.sizeY-1), dtype=np.double) * g.Cdtds / imp0
    Hy = np.zeros((g.sizeX-1, g.sizeY), dtype=np.double)
    Chyh = np.ones((g.sizeX-1, g.sizeY), dtype=np.double)
    Chye = np.ones((g.sizeX-1, g.sizeY), dtype=np.double) * g.Cdtds / imp0
    Ez = np.zeros((g.max_time, g.sizeX, g.sizeY), dtype=np.double)
    Ceze = np.ones((g.sizeX, g.sizeY), dtype=np.double)
    Cezh = np.ones((g.sizeX, g.sizeY), dtype=np.double) * g.Cdtds * imp0

    # Create pointers to Numpy arrays
    Hx_ptr = Hx.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    Chxh_ptr = Chxh.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    Chxe_ptr = Chxe.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    Hy_ptr = Hy.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    Chyh_ptr = Chyh.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    Chye_ptr = Chye.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    Ez_ptr = Ez.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    Ceze_ptr = Ceze.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    Cezh_ptr = Cezh.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

    # Store pointers to arrays in struct Grid
    g.Hx = Hx_ptr
    g.Chxh = Chxh_ptr
    g.Chxe = Chxe_ptr
    g.Hy = Hy_ptr
    g.Chyh = Chyh_ptr
    g.Chye = Chye_ptr
    g.Ez = Ez_ptr
    g.Ceze = Ceze_ptr
    g.Cezh = Cezh_ptr

    # Return class containing Numpy arrays for use in Python code
    return ArrayStorage(Hx, Chxh, Chxe, Hy, Chyh, Chye, Ez, Ceze, Cezh)
