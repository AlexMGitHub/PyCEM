"""Page for Total Field/Scattered Field 2D FDTD simulation."""
# %% Imports
# Standard system imports

# Related third party imports
from dash import html, Input, Output, State
import dash_bootstrap_components as dbc

# Local application/library specific imports
from webapp.app import app
from webapp.pages.styling import content_style
from pycem.fdtd_scenarios import TFSFPlate, Grid
from pycem.fdtd_pyvista import save_mesh_movie
from pycem.utilities import get_project_root


# %% Globals
scenario = TFSFPlate(Grid())


# %% Dash Components
sim_card = dbc.Card(
    dbc.CardBody(
        [
            html.H4(scenario.title, className="card-title"),
            html.P(scenario.description),
            html.Div([
                dbc.Row([
                    dbc.Col(dbc.Button(id=f'simulate-{scenario.name}-button',
                                       n_clicks=0,
                                       children='Simulate',
                                       color="success",
                                       class_name="my-2"
                                       )
                            ),
                    dbc.Col(html.P(id=f'sim-state-{scenario.name}',
                                   children=["Simulation not run"]
                                   )
                            ),
                    dbc.Col(html.Progress(id=f"sim-progress-bar-{scenario.name}",
                                          style={'visibility': 'hidden'}
                                          ),
                            )
                ], class_name="my-2"),

                dbc.Row([
                    dbc.Col(dbc.Button(id=f'animate-{scenario.name}-button',
                                       n_clicks=0,
                                       children='Create Animation',
                                       disabled=False,
                                       color="danger",
                                       class_name="my-2"
                                       )
                            ),
                    dbc.Col(html.P(id=f"anim-state-{scenario.name}",
                                   children="Animation not run"
                                   ),
                            ),
                    dbc.Col(html.Progress(id=f"anim-progress-bar-{scenario.name}",
                                          style={'visibility': 'hidden'}
                                          ),
                            )
                ],),
            ]
            ),
        ]),
)

anim_card = dbc.Card(
    dbc.CardBody(
        [
            html.H4(f"{scenario.title} Animation", className="card-title"),
            html.Div([
                html.Video(id=f'mesh-video-{scenario.name}',
                           src=app.get_asset_url(
                               f'mov/fdtd/{scenario.name}.mp4'),
                           width=500,
                           controls=True,
                           autoPlay=True,
                           loop=True
                           )
            ],
            )
        ]
    )
)


# %% Dash app layout
content = html.Div(children=[
    dbc.Row(
        [
            dbc.Col(sim_card, width=5),
            dbc.Col(anim_card, width=7),
        ],
    )], style=content_style)


# %% Callbacks
@app.callback(
    Output(component_id=f'sim-state-{scenario.name}',
           component_property='children'),
    Input(f'simulate-{scenario.name}-button', 'n_clicks'),
    prevent_initial_call=True,
)
def run_tfsf_simulation(n_clicks):
    """Run the C code to simulate the FDTD scenario."""
    scenario.run_sim()
    return 'Simulation complete!'


@app.long_callback(
    Output(component_id=f'anim-state-{scenario.name}',
           component_property='children'),
    Output(
        component_id=f'mesh-video-{scenario.name}', component_property='src'),
    Input(f'animate-{scenario.name}-button', 'n_clicks'),
    State(f'simulate-{scenario.name}-button', 'n_clicks'),
    running=[
        (Output(f"animate-{scenario.name}-button", "disabled"), True, False),
        (
            Output(f"anim-state-{scenario.name}", "style"),
            {"visibility": "hidden"},
            {"visibility": "visible"},
        ),
        (
            Output(f"anim-progress-bar-{scenario.name}", "style"),
            {"visibility": "visible"},
            {"visibility": "hidden"},
        ),
    ],
    progress=[Output(f"anim-progress-bar-{scenario.name}", "value"),
              Output(f"anim-progress-bar-{scenario.name}", "max")],
    prevent_initial_call=True,
    interval=300
)
def create_tfsf_animations(set_progress, n_clicks, sim_n_clicks):
    """Create PyVista animation of FDTD scenario if it does not exist."""
    if n_clicks > 0 and sim_n_clicks == 0:
        return ('Run sim first!', '')  # User clicked animate before sim
    webapp_path_to_mov = f'mov/fdtd/{scenario.name}.mp4'
    root = get_project_root()
    project_path_to_mov = root / 'src/webapp/assets' / webapp_path_to_mov
    if sim_n_clicks == 0 and not project_path_to_mov.is_file():
        return ('Animation not run', '')  # If anim doesn't already exist
    save_mesh_movie(project_path_to_mov, scenario, set_progress)
    return ('Animation created!', app.get_asset_url(webapp_path_to_mov))
