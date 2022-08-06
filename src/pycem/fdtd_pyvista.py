"""Contains functions for plotting meshes using PyVista."""
# %% Imports
# Standard system imports

# Related third party imports
import numpy as np
import pyvista as pv

# Local application/library specific imports


# %% Globals
fdtd_theme = pv.themes.DefaultTheme()
fdtd_theme.cmap = 'jet'
fdtd_theme.show_edges = True


# %% PyVista Plotting Functions
def log_norm(data, z_norm=1):
    """Return log normalized matrix."""
    return np.log10(np.abs((data)/z_norm)+np.nextafter(0, 1))


def save_mesh_png(filepath, scenario, frame=0, clim=[-3, 0]):
    """Create a .PNG image of a PyVista mesh at a specified frame."""
    # Create the spatial reference
    grid = pv.UniformGrid()

    # Set the grid dimensions: shape + 1 because we want to inject our values
    # on the CELL data
    grid.dimensions = np.array((scenario.g.sizeX, scenario.g.sizeY, 1)) + 1

    # Edit the spatial reference
    grid.origin = (0, 0, 0)  # The bottom left corner of the data set
    grid.spacing = (1, 1, 0)  # These are the cell sizes along each axis

    # Get data from simulation results
    values = log_norm(scenario.arr.Ez[frame, :, :])

    # Add the data values to the cell data
    grid.cell_data["values"] = values.flatten(order="F")  # Flatten the array!

    pl = pv.Plotter(off_screen=True)
    pl.theme = fdtd_theme
    pl.add_mesh(grid, show_edges=False, clim=clim, lighting=False)
    pl.add_axes_at_origin(labels_off=True)
    pl.view_xy()

    # Now plot the grid!
    # Recommended by docs prior to taking screenshot
    pl.show(auto_close=False)
    # pl.show(window_size=(500, 500), screenshot=filepath)
    pl.show(screenshot=filepath)


def save_mesh_movie(filepath_mov, scenario, set_progress, clim=[-3, 0]):
    """Create a .MP4 animation of a PyVista mesh."""
    if filepath_mov.is_file():
        return

    # Create the spatial reference
    grid = pv.UniformGrid()

    # Set the grid dimensions: shape + 1 because we want to inject our values
    # on the CELL data
    grid.dimensions = np.array((scenario.g.sizeX, scenario.g.sizeY, 1)) + 1

    # Edit the spatial reference
    grid.origin = (0, 0, 0)  # The bottom left corner of the data set
    grid.spacing = (1, 1, 0)  # These are the cell sizes along each axis

    # Get data from simulation results
    values = scenario.arr.Ez[0, :, :]
    grid.cell_data["values"] = values.flatten(order="F")

    pl = pv.Plotter(off_screen=True)
    pl.theme = fdtd_theme
    pl.add_mesh(grid, show_edges=False, clim=clim, lighting=False)
    pl.add_axes_at_origin(labels_off=True)
    pl.view_xy()

    pl.open_movie(filepath_mov)
    for i in range(scenario.g.max_time):
        values = log_norm(scenario.arr.Ez[i, :, :])
        pl.update_scalars(values.flatten(order="F"))
        pl.render()
        pl.write_frame()
        set_progress((str(i + 1), str(scenario.g.max_time)))
    pl.close()
