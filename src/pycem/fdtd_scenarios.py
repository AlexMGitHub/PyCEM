"""Contains Python classes representing FDTD simulation scenarios."""
# %% Imports
# Standard system imports
import ctypes
from pathlib import Path

# Related third party imports
import numpy as np
import pyvista as pv

# Local application/library specific imports
from pycem.utilities import get_project_root


# %% Simulation Classes
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

    name = 'RickerTMz2D'            # Scenario name
    image_frame = 50                # Frame to use for scenario image
    sizeX = 101                     # X size of domain
    sizeY = 81                      # Y size of domain
    max_time = 300                  # Duration of simulation
    Cdtds = 1.0 / np.sqrt(2.0)      # Courant number
    href = '/ricker'                  # Webapp URL
    title = "Ricker Wavelet"
    description = """
        This scenario simulates a Ricker Wavelet source at the center of a 2D
        grid.  The edges of the grid have a perfect electric conductor (PEC) 
        boundary that reflects the radiated waves.
        """

    def __init__(self, g):
        """Initialize the FDTD grid and any update functions."""
        g.sizeX = RickerTMz2D.sizeX         # X size of domain
        g.sizeY = RickerTMz2D.sizeY         # Y size of domain
        g.time = 0                          # Current time step
        g.max_time = RickerTMz2D.max_time   # Duration of simulation
        g.Cdtds = RickerTMz2D.Cdtds         # Courant number
        self.arr = ArrayStorage(g)          # Initialize E and H-field arrays
        self.g = g
        self.init_c_funcs()                 # Initialize C foreign function

    def init_c_funcs(self):
        """Specify order of C functions used in scenario."""
        root = get_project_root()
        lib_path = root / 'src/C/lib/libFDTD_TMz.so'
        c_lib = ctypes.CDLL(lib_path)
        self.scenarioRicker = c_lib.scenarioRicker
        self.scenarioRicker.argtypes = [ctypes.POINTER(Grid)]
        self.scenarioRicker.restype = None

    def run_sim(self):
        """Run simulation by calling C foreign function."""
        self.scenarioRicker(self.g)


class TFSFSource:
    """Simulate a TMz 2D FDTD grid with a TF/SF source.

    TFSF source offset by 5 nodes from the edge of the grid.

    Replicates figure 8.6 from John B. Schneider's textbook "Understanding the
    Finite-Difference Time-Domain Method."
    """

    name = 'TFSFSource'             # Scenario name
    image_frame = 100               # Frame to use for scenario image
    sizeX = 101                     # X size of domain
    sizeY = 81                      # Y size of domain
    max_time = 300                  # Duration of simulation
    Cdtds = 1.0 / np.sqrt(2.0)      # Courant number
    href = '/tfsf'                  # Webapp URL
    title = "TF/SF"
    description = """
        This scenario simulates a Total Field/Scattered Field
        wave traveling across a 2D grid.  The edges of the 
        grid have an absorbing boundary condition (ABC) to 
        capture the radiated waves.
        """

    def __init__(self, g):
        """Initialize the FDTD grid and any update functions."""
        g.sizeX = TFSFSource.sizeX          # X size of domain
        g.sizeY = TFSFSource.sizeY          # Y size of domain
        g.time = 0                          # Current time step
        g.max_time = TFSFSource.max_time    # Duration of simulation
        g.Cdtds = TFSFSource.Cdtds          # Courant number
        self.arr = ArrayStorage(g)          # Initialize E and H-field arrays
        self.g = g
        self.init_c_funcs()                 # Initialize C foreign function

    def init_c_funcs(self):
        """Specify order of C functions used in scenario."""
        root = get_project_root()
        lib_path = root / 'src/C/lib/libFDTD_TMz.so'
        c_lib = ctypes.CDLL(lib_path)
        self.scenarioTFSF = c_lib.scenarioTFSF
        self.scenarioTFSF.argtypes = [ctypes.POINTER(Grid)]
        self.scenarioTFSF.restype = None

    def run_sim(self):
        """Run simulation by calling C foreign function."""
        self.scenarioTFSF(self.g)


class TFSFPlate:
    """Simulate a TMz 2D FDTD grid with a TF/SF source.

    TFSF source offset by 5 nodes from the edge of the grid.

    Replicates figure 8.6 from John B. Schneider's textbook "Understanding the
    Finite-Difference Time-Domain Method."
    """

    name = 'TFSFPlate'              # Scenario name
    image_frame = 50                # Frame to use for scenario image
    sizeX = 101                     # X size of domain
    sizeY = 81                      # Y size of domain
    max_time = 300                  # Duration of simulation
    Cdtds = 1.0 / np.sqrt(2.0)      # Courant number
    href = '/tfsf_plate'              # Webapp URL
    title = "TF/SF Plate"
    description = """
        This scenario simulates a Total Field/Scattered Field
        wave impinging on a vertical PEC plate.  The edges of the 
        grid have an absorbing boundary condition (ABC) to 
        capture the radiated waves.
        """

    def __init__(self, g):
        """Initialize the FDTD grid and any update functions."""
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


class TFSFDisk:
    """Simulate a TMz 2D FDTD grid with a TF/SF source.

    TFSF source offset by 5 nodes from the edge of the grid.

    Replicates figure 8.6 from John B. Schneider's textbook "Understanding the
    Finite-Difference Time-Domain Method."
    """

    name = 'TFSFDisk'             # Scenario name
    image_frame = 50                # Frame to use for scenario image
    sizeX = 101                     # X size of domain
    sizeY = 81                      # Y size of domain
    max_time = 300                  # Duration of simulation
    Cdtds = 1.0 / np.sqrt(2.0)      # Courant number
    href = '/tfsf_disk'               # Webapp URL
    title = "TF/SF Disk"
    description = """
        This scenario simulates a Total Field/Scattered Field
        wave impinging on a circular PEC desk.  The edges of the 
        grid have an absorbing boundary condition (ABC) to 
        capture the radiated waves.
        """

    def __init__(self, g):
        """Initialize the FDTD grid and any update functions."""
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


fdtd_scenario_list = (RickerTMz2D, TFSFSource, TFSFPlate, TFSFDisk)
fdtd_scenario_dict = {
    scenario.title: scenario for scenario in fdtd_scenario_list}
