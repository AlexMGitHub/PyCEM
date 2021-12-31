# %% Imports
# Standard system imports

# Related third party imports
import numpy as np
import pytest

# Local application/library specific imports
from pycem.clib_wrapper import CLib_Wrapper


# %% Tests
def test_matrix_mult():
    """Test wrapper around matrix multiplication C function."""
    # Create random matrices to multiply
    rng = np.random.default_rng(12345)
    mat1 = rng.random((20, 10), dtype=np.double)
    mat2 = rng.random((10, 15), dtype=np.double)
    clib = CLib_Wrapper()

    c_result = clib.mat_mult_wrapper(mat1, mat2)
    python_result = mat1 @ mat2

    np.testing.assert_allclose(python_result, c_result, rtol=0, atol=1e-10)


def test_matrix_mult_invalid():
    """Provide invalid inputs to wrapper around matrix mult C function."""
    rng = np.random.default_rng(12345)
    clib = CLib_Wrapper()

    # Create matrices with invalid inner dimensions
    mat1 = rng.random((20, 10), dtype=np.double)
    mat2 = rng.random((12, 15), dtype=np.double)
    with pytest.raises(Exception):
        result = clib.mat_mult_wrapper(mat1, mat2)

    # Create matrix with invalid data type
    mat2 = np.ones((10, 15), dtype=int)
    with pytest.raises(Exception):
        result = clib.mat_mult_wrapper(mat1, mat2)
