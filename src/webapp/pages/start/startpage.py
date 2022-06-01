"""Start page for PyCEM web app."""
# %% Imports
# Standard system imports

# Related third party imports
from dash import html
import dash_bootstrap_components as dbc

# Local application/library specific imports
from webapp.pages.styling import content_style, sidebar_div_style, \
    sidebar_style, paragraph_style


# %% Dash app layout
list_group = html.Div(id='list-group')

fdtd_list_group = dbc.ListGroup(
    [
        html.Div(
            html.P(
                "2D Simulations", style=paragraph_style
            ), style=sidebar_div_style
        ),
        dbc.NavLink(
            "Ricker Wavelet", href="/ricker",  # color="secondary",
            active="exact",
            id="ricker",
        ),
        dbc.NavLink(
            "TF/SF", href="/tfsf",  # color="secondary",
            active="exact",
            id="tfsf"
        ),
        dbc.NavLink(
            "TF/SF Plate", href="/tfsf_plate",  # color="secondary",
            active="exact",
            id="tfsf_plate"
        ),
        dbc.NavLink(
            "TF/SF Disk", href="/tfsf_disk",  # color="secondary",
            active="exact",
            id="tfsf_disk"
        ),
        html.Div(
            html.P(
                "3D Simulations", style=paragraph_style
            ), style=sidebar_div_style
        ),
    ]
)

sidebar = html.Div(
    [
        html.H2(html.A("PyCEM", href='/'), className="display-4"),
        html.Hr(),
        html.P(
            "Choose a solver and a scenario to begin.", className="lead"
        ),
        dbc.Nav(
            [
                dbc.DropdownMenu(
                    children=[
                        dbc.DropdownMenuItem(
                            "FDTD", id='fdtd-solver', n_clicks=0,
                            href='/fdtd'),
                        dbc.DropdownMenuItem(
                            "MoM", id='mom-solver', n_clicks=0),
                        dbc.DropdownMenuItem(
                            "FEM", id='fem-solver', n_clicks=0),
                    ],
                    label="CEM Solver",
                    color="info",
                    id='solver-select'
                ),
                list_group

            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=sidebar_style, className="bg-light"
)

content = html.Div([
    html.H3('Start page'),
], id='content', style=content_style)

layout = html.Div([sidebar, content], style=content_style)
