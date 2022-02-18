"""Contains classes and functions used by the FDTD simulation."""
# %% Imports
# Standard system imports
import ctypes

# Related third party imports
import numpy as np

# Local application/library specific imports
from pycem.utilities import get_project_root


# %% General Classes
class ArrayStorage:
    """Initializes and stores E-Field and H-Field arrays."""

    def __init__(self, g):
        imp0 = 377.0  # Impedance of free space
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
        # Store arrays in class instance
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


# %% Scenarios
class RickerTMz2D:
    """Simulate a TMz 2D FDTD grid with a Ricker wavelet.

    Ricker wavelet modeled as a hard source at the center of the grid.

    From section 8.4 of John B. Schneider's textbook "Understanding the
    Finite-Difference Time-Domain Method."
    """

    def __init__(self, g):
        """Initialize the FDTD grid and any update functions."""
        self.imp0 = 377.0               # Impedance of free space
        g.sizeX = 101                   # X size of domain
        g.sizeY = 81                    # Y size of domain
        g.time = 0                      # Current time step
        g.max_time = 300                # Duration of simulation
        g.Cdtds = 1.0 / np.sqrt(2.0)    # Courant number
        self.arr = ArrayStorage(g)      # Initialize E and H-field arrays
        self.g = g
        self.init_funcs()               # Initialize C foreign function

    def init_funcs(self):
        """Specify order of C functions used in scenario."""
        root = get_project_root()
        lib_path = root / 'src/C/lib/libFDTD_TMz.so'
        c_lib = ctypes.CDLL(lib_path)
        self.rickerTMz2D = c_lib.rickerTMz2D
        self.rickerTMz2D.argtypes = [ctypes.POINTER(Grid)]
        self.rickerTMz2D.restype = None

    def run_sim(self):
        """Run simulation by calling C foreign function."""
        self.rickerTMz2D(self.g)


class TFSFSource:
    """Simulate a TMz 2D FDTD grid with a TF/SF source.

    TFSF source offset by 5 nodes from the edge of the grid.

    Replicates figure 8.6 from John B. Schneider's textbook "Understanding the
    Finite-Difference Time-Domain Method."
    """

    def __init__(self, g):
        """Initialize the FDTD grid and any update functions."""
        self.imp0 = 377.0               # Impedance of free space
        g.sizeX = 101                   # X size of domain
        g.sizeY = 81                    # Y size of domain
        g.time = 0                      # Current time step
        g.max_time = 300                # Duration of simulation
        g.Cdtds = 1.0 / np.sqrt(2.0)    # Courant number
        self.arr = ArrayStorage(g)      # Initialize E and H-field arrays
        self.g = g
        self.init_funcs()               # Initialize C foreign function

    def init_funcs(self):
        """Specify order of C functions used in scenario."""
        root = get_project_root()
        lib_path = root / 'src/C/lib/libFDTD_TMz.so'
        c_lib = ctypes.CDLL(lib_path)
        self.rickerTMz2D = c_lib.rickerTMz2D
        self.rickerTMz2D.argtypes = [ctypes.POINTER(Grid)]
        self.rickerTMz2D.restype = None

    def run_sim(self):
        """Run simulation by calling C foreign function."""
        self.rickerTMz2D(self.g)
