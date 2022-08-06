"""Generate thumbnail images for simulation scenarios."""
# %% Imports
# Standard system imports

# Related third party imports

# Local application/library specific imports
from pycem.utilities import get_project_root
from pycem.fdtd_scenarios import Grid, fdtd_scenario_list
from pycem.fdtd_pyvista import save_mesh_png


# %% Functions
def create_fdtd_images():
    """Create image previews for FDTD scenarios if they don't exist."""
    for scenario in fdtd_scenario_list:
        g = Grid()
        scenario_init = scenario(g)
        filename = get_project_root() / \
            f'src/webapp/assets/img/fdtd/{scenario_init.name}.png'
        if not filename.is_file():
            scenario_init.run_sim()
            frame = scenario_init.image_frame
            save_mesh_png(filename, scenario_init, frame)


if __name__ == '__main__':
    create_fdtd_images()
