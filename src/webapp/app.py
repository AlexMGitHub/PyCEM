"""Declare app as required for multi-page apps with long_callback()."""
# %% Imports
# Standard system imports
from pathlib import Path

# Related third party imports
from dash import Dash
from dash.long_callback import DiskcacheLongCallbackManager
import dash_bootstrap_components as dbc
import diskcache

# Local application/library specific imports


# %% Instantiate Dash app
# Pickle protocol must be <= 4
cache = diskcache.Cache("./cache", disk_pickle_protocol=4)
long_callback_manager = DiskcacheLongCallbackManager(cache)

app = Dash(__name__,
           long_callback_manager=long_callback_manager,
           external_stylesheets=[dbc.themes.FLATLY],
           suppress_callback_exceptions=True,
           prevent_initial_callbacks=True
           )
