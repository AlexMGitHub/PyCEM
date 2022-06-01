"""Declare app as required for multi-page apps with long_callback()."""

# Related third party imports
from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
from dash.long_callback import DiskcacheLongCallbackManager
import dash_bootstrap_components as dbc
import diskcache


# Pickle protocol must be <= 4
cache = diskcache.Cache("./cache", disk_pickle_protocol=4)
long_callback_manager = DiskcacheLongCallbackManager(cache)

app = Dash(__name__,
           long_callback_manager=long_callback_manager,
           external_stylesheets=[dbc.themes.FLATLY],
           suppress_callback_exceptions=True,
           prevent_initial_callbacks=True
           )