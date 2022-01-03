"""Python wrapper for C library functions used for benchmarking."""

# %% Imports
# Standard system imports
import ctypes
from pathlib import Path

# Related third party imports
import numpy as np

# Local application/library specific imports
from pycem.utilities import get_project_root


# %% Classes
class CLib_Wrapper:
    def __init__(self):
        """Initialize C library and argument data types of its functions."""
        root = get_project_root()
        lib_path = root / 'src/C/lib/libbenchmarking.so'
        self.c_lib = ctypes.CDLL(lib_path)

        # Matrix multiplication function
        self.mat_mult = self.c_lib.mat_mult
        self.mat_mult.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                  ctypes.POINTER(ctypes.c_double),
                                  ctypes.POINTER(ctypes.c_double),
                                  ctypes.POINTER(ctypes.c_double)]
        self.mat_mult.restype = None  # C function returns void

    def mat_mult_wrapper(self, mat1, mat2):
        """Return product of two matrices."""
        out1, inner1 = mat1.shape
        inner2, out2 = mat2.shape

        assert inner1 == inner2, 'Matrix inner dimensions must match!'
        assert mat1.dtype == mat2.dtype == np.double, 'Dtype must be np.double'

        mat3 = np.empty((out1, out2), dtype=np.double)
        mat1_ptr = mat1.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        mat2_ptr = mat2.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        mat3_ptr = mat3.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

        self.mat_mult(out1, out2, inner1, mat1_ptr, mat2_ptr, mat3_ptr)

        return mat3


if __name__ == "__main__":
    # Create small random matrices to multiply
    rng = np.random.default_rng(12345)
    mat1 = rng.random((2, 3), dtype=np.double)
    mat2 = rng.random((3, 4), dtype=np.double)
    clib = CLib_Wrapper()

    print('\nC library answer:')
    c_result = clib.mat_mult_wrapper(mat1, mat2)
    print(c_result)

    print('\nPython answer:')
    python_result = mat1 @ mat2
    print(python_result)

    np.testing.assert_allclose(python_result, c_result, rtol=0, atol=1e-10)
