# %% Imports
# Standard system imports

# Related third party imports
from dash import get_asset_url, html
import dash_bootstrap_components as dbc

# Local application/library specific imports
from webapp.app import app
from pycem.fdtd_scenarios import fdtd_scenario_list
from webapp.pages.styling import content_style


# %% Generate cards depicting FDTD scenarios
cards = [
    dbc.Card(
        [
            dbc.CardImg(src=get_asset_url(f'img/fdtd/{scenario.name}.png'),
                        top=True),
            dbc.CardBody(
                [
                    html.H4(scenario.title, className="card-title"),
                    html.P(scenario.description, className="card-text"),
                    dbc.Button("Click here",
                               href=scenario.href,
                               color="primary",
                               class_name="mt-auto mx-auto w-50"
                               ),
                ], className="d-flex flex-column"
            ),
        ], color="light", class_name="mx-2")
    for scenario in fdtd_scenario_list
]


# %% Dash app layout
content = html.Div(children=[dbc.CardGroup(cards)], style=content_style)
