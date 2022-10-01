"""Start page for PyCEM web app."""
# %% Imports
# Standard system imports

# Related third party imports
from dash import html
import dash_bootstrap_components as dbc

# Local application/library specific imports
from pycem.fda_scenarios import fda_scenario_list
from pycem.fdtd_scenarios import fdtd_scenario_list
from webapp.pages.styling import content_style, sidebar_div_style, \
    sidebar_style, paragraph_style


# %% Dash app layout
# By default navbar content is blank until a solver is selected
list_group = html.Div(id='list-group')

# FDTD navbar content
fdtd_2d_header = html.Div(
    html.P(
        "2D Simulations", style=paragraph_style
    ), style=sidebar_div_style
)

fdtd_2d_scenarios = [
    dbc.NavLink(
        scenario.title, href=scenario.href,
        active="exact",
        id=scenario.title[1:],
    ) for scenario in fdtd_scenario_list]

fdtd_3d_header = html.Div(
    html.P(
        "3D Simulations", style=paragraph_style
    ), style=sidebar_div_style
)

fdtd_list_group = dbc.ListGroup(
    [
        fdtd_2d_header,
        fdtd_3d_header,
    ]
)

fdtd_list_group.children[1:1] = fdtd_2d_scenarios  # Insert scenarios in list


# FDA navbar content
fda_tl_header = html.Div(
    html.P(
        "TLine Simulations", style=paragraph_style
    ), style=sidebar_div_style
)

fda_tl_scenarios = [
    dbc.NavLink(
        scenario.title, href=scenario.href,
        active="exact",
        id=scenario.title[1:],
    ) for scenario in fda_scenario_list]

fda_list_group = dbc.ListGroup(
    [
        fda_tl_header
    ]
)

fda_list_group.children[1:1] = fda_tl_scenarios  # Insert scenarios in list


# Sidebar content
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
                            "FDA", id='fda-solver', n_clicks=0,
                            href='/fda'),
                        dbc.DropdownMenuItem(
                            "FDTD", id='fdtd-solver', n_clicks=0,
                            href='/fdtd'),
                        dbc.DropdownMenuItem(
                            "MoM", id='mom-solver', n_clicks=0,
                            href='/mom'),
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

# Start page content
content = html.Div([
    html.H3('Welcome to PyCEM!'),
], id='content', style=content_style)

layout = html.Div([sidebar, content], style=content_style)
