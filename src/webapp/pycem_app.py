"""Web app user interface to PyCEM simulations."""
# %% Imports
# Standard system imports
import os

# Related third party imports
from dash import html, dcc
from dash.dependencies import Input, Output

# Local application/library specific imports
from webapp.app import app
from webapp.pages.fda import (
    fda_cards, symmetric_stripline, microstrip, coaxial, asymmetric_stripline,
    differential_microstrip, broadside_stripline, differential_stripline)
from webapp.pages.fdtd import (
    ricker, tfsf, tfsf_corner_reflector, tfsf_plate, tfsf_disk, tfsf_minefield,
    fdtd_cards)
from webapp.pages.start import startpage
from webapp.pages.styling import content_style


# %% Dash app layout
app.title = 'PyCEM'

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div([startpage.sidebar, html.Div(id='page-content')])
])


# %% Generate dict of FDTD Scenario URLs to page content
fdtd_page_list = (ricker, tfsf, tfsf_plate, tfsf_disk, tfsf_corner_reflector,
                  tfsf_minefield)
fdtd_page_dict = {page.scenario.href: (page.content, startpage.fdtd_list_group)
                  for page in fdtd_page_list}


# %% Generate dict of FDA Scenario URLs to page content
fda_page_list = (symmetric_stripline, microstrip, coaxial,
                 asymmetric_stripline, differential_microstrip,
                 broadside_stripline, differential_stripline)
fda_page_dict = {page.scenario.href: (page.content, startpage.fda_list_group)
                 for page in fda_page_list}


# %% App URLs
@app.callback(Output('page-content', 'children'),
              Output('list-group', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    """Return appropriate page content when URL is changed."""
    if pathname == '/':
        return startpage.content, startpage.list_group
    elif pathname == '/fdtd':
        return fdtd_cards.content, startpage.fdtd_list_group
    elif pathname in fdtd_page_dict:
        return fdtd_page_dict[pathname]
    elif pathname == '/fda':
        return fda_cards.content, startpage.fda_list_group
    elif pathname in fda_page_dict:
        return fda_page_dict[pathname]
    else:
        return (html.Div(html.P('404'), style=content_style),
                startpage.fdtd_list_group)


if __name__ == '__main__':
    server_mode = os.environ['SERVER_DEBUG_MODE']
    if server_mode == 'debug':
        DEBUG_MODE = True
    else:
        DEBUG_MODE = False
    app.run(host='0.0.0.0', port='8050', debug=DEBUG_MODE)
