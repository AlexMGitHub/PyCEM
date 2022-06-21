# %% Imports
# Standard system imports

# Related third party imports
from dash import get_asset_url, html
import dash_bootstrap_components as dbc
import numpy as np

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
        ], color="light", class_name="mx-2 my-2")
    for scenario in fdtd_scenario_list
]

# Wrap cards into a new card group every four cards, so there are four per row
CARDS_PER_ROW = 4
mod_cards = len(cards) % 4
if mod_cards != 0:  # Add blank cards to fill row
    for _ in range(CARDS_PER_ROW - mod_cards):
        cards.append(dbc.Card(class_name="mx-2 my-2"))

num_card_groups = int(len(cards) / CARDS_PER_ROW)

card_groups = [dbc.CardGroup(cards[CARDS_PER_ROW*group:CARDS_PER_ROW*(group+1)])
               for group in range(num_card_groups)]


# %% Dash app layout
content = html.Div(children=card_groups, style=content_style)
