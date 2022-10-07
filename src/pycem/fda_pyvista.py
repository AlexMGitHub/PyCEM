"""Contains functions for plotting meshes for FDA using PyVista."""
# %% Imports
# Standard system imports

# Related third party imports
import numpy as np
import pyvista as pv

# Local application/library specific imports


# %% Globals
fda_theme = pv.themes.DefaultTheme()
fda_theme.colorbar_horizontal.position_y = 0.2


# %% PyVista Plotting Functions
def log_norm(data, z_norm=1):
    """Return bi-symmetric log normalized matrix allowing negative values."""
    return np.sign(data) * np.log10(1+np.abs(data)/10**z_norm)


def save_mesh_png(data, Nx, Ny, dx, dy, filepath, clim=None, cmap='turbo',
                  log=False, show_edges=True):
    """Create a .PNG image of a PyVista mesh."""
    if clim is None:
        clim = [0, 1]

    # Re-arrange data so that PyVista plots it correctly
    values = data.reshape((Ny, Nx))
    values = np.flip(values, axis=0).flatten()

    # Create the spatial reference
    grid = pv.UniformGrid()

    # Set the grid dimensions: shape + 1 because we want to inject our values
    # on the CELL data
    grid.dimensions = np.array((Nx, Ny, 1)) + 1

    # Edit the spatial reference
    grid.origin = (0, 0, 0)  # The bottom left corner of the data set
    # These are the cell sizes along each axis
    grid.spacing = (1, dy/dx, 0)

    # Add the data values to the cell data
    if log:
        log_values = log_norm(values)
        grid.cell_data["values"] = log_values
        clim = [np.min(log_values), np.max(log_values)]
    else:
        grid.cell_data["values"] = values

    pl = pv.Plotter(off_screen=True)
    pl.theme = fda_theme
    pl.add_mesh(grid, show_edges=show_edges, clim=clim, lighting=False,
                cmap=cmap)
    pl.add_axes_at_origin(labels_off=True)
    pl.view_xy()

    # Save image of grid to file
    pl.show(screenshot=filepath)
