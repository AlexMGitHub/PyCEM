"""Web app user interface to PyCEM simulations."""
# %% Imports
# Standard system imports

# Related third party imports
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# Local application/library specific imports
from webapp.app import app
from webapp.pages.fdtd import ricker, tfsf, fdtd_cards
from webapp.pages.start import startpage
from webapp.pages.styling import content_style
from pycem.fdtd_scenarios import fdtd_scenario_list
from pycem.utilities import get_project_root


# %% Dash app layout
app.title = 'PyCEM'

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div([startpage.sidebar, html.Div(id='page-content')])
])


@app.callback(Output('page-content', 'children'),
              Output('list-group', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/':
        return startpage.content, startpage.list_group
    elif pathname == '/fdtd':
        return fdtd_cards.content, startpage.fdtd_list_group
    elif pathname == '/ricker':
        return ricker.content, startpage.fdtd_list_group
    elif pathname == '/tfsf':
        return tfsf.content, startpage.fdtd_list_group
    else:
        return (html.Div(html.P('404'), style=content_style),
                startpage.fdtd_list_group)


if __name__ == '__main__':
    app.run_server(debug=True)
