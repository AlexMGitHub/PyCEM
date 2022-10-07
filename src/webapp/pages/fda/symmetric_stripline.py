"""Page for symmetric stripline FDA simulation."""
# %% Imports
# Standard system imports

# Related third party imports
from dash import html, Input, Output, State, ctx
import dash_bootstrap_components as dbc

# Local application/library specific imports
from webapp.app import app
from webapp.pages.styling import content_style
from pycem.fda_scenarios import SymmetricStripline
from pycem.utilities import get_project_root, list_files


# %% Globals
scenario = SymmetricStripline()


# %% Dash Components
sim_card = dbc.Card(
    dbc.CardBody(
        [
            html.H4(scenario.title, className="card-title"),
            html.P(scenario.description),
            html.Div([
                dbc.Row([
                    dbc.Col(dbc.Button(id=f'calc-{scenario.name}-button',
                                       n_clicks=0,
                                       children='Analytical Solution',
                                       disabled=False,
                                       color="danger",
                                       class_name="my-2"
                                       )
                            ),
                ],),
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
                    dbc.Col(html.Progress(
                        id=f"sim-progress-bar-{scenario.name}",
                        style={'visibility': 'hidden'}
                    ),
                    )
                ], class_name="my-2"),
            ]
            ),
        ]),
)


# %% Image Carousel
diagram_dict = {"key": "1",
                "src": app.get_asset_url(
                    f"img/fda/diagrams/{scenario.name}.png")}

carousel = dbc.Carousel(
    items=[diagram_dict],
    controls=True,
    indicators=True,
    id=f'carousel-{scenario.name}'
)


# %% Form components
width_input = html.Div(
    [
        dbc.Label("Width (W)", html_for=f"width-input-{scenario.name}"),
        dbc.Input(type="number",
                  id=f"width-input-{scenario.name}",
                  min=0,
                  step=0.001,
                  value=0.35),
        dbc.FormText(
            "Enter the width of the trace in millimeters.",
            color="secondary",
        ),
    ],
    className="mb-3",
)

height_input = html.Div(
    [
        dbc.Label("Height (H)", html_for=f"height-input-{scenario.name}"),
        dbc.Input(
            type="number",
            id=f"height-input-{scenario.name}",
            min=0,
            step=0.001,
            value=0.9
        ),
        dbc.FormText(
            "Enter the height of the substrate in millimeters.",
            color="secondary"
        ),
    ],
    className="mb-3",
)

dy_input = html.Div(
    [
        dbc.Label("Trace Thickness (T)", html_for=f"dy-input-{scenario.name}"),
        dbc.Input(
            type="number",
            id=f"dy-input-{scenario.name}",
            min=0,
            step=0.001,
            value=0.025
        ),
        dbc.FormText(
            "Enter the thickness of the trace in millimeters.  This is also "
            "the size of the grid cell in the Y-direction.",
            color="secondary"
        ),
    ],
    className="mb-3",
)

er_input = html.Div(
    [
        dbc.Label("Dielectric Constant (Er)",
                  html_for=f"er-input-{scenario.name}"),
        dbc.Input(
            type="number",
            id=f"er-input-{scenario.name}",
            min=0,
            step=0.001,
            value=4
        ),
        dbc.FormText(
            "Enter the dielectric constant of the substrate material.",
            color="secondary"
        ),
    ],
    className="mb-3",
)

dx_input = html.Div(
    [
        dbc.Label("X-direction grid cell size (dx)",
                  html_for=f"dx-input-{scenario.name}"),
        dbc.Input(
            type="number",
            id=f"dx-input-{scenario.name}",
            min=0,
            step=0.001,
            value=0.025
        ),
        dbc.FormText(
            "Enter size of the grid cell in the X-direction (horizontal).",
            color="secondary"
        ),
    ],
    className="mb-3",
)

form = dbc.Form([width_input, height_input, dy_input, er_input, dx_input])

form_card = dbc.Card(
    dbc.CardBody(
        [
            html.P(
                "Refer to the diagram to the right and enter the transmission "
                "line parameters in the form below."),
            html.Div([form])
        ]))

# %% Results table
table_header = [
    html.Thead(html.Tr(
        [html.Th("Quantity"),
         html.Th("Analytical Formula"),
         html.Th("FDA Simulation"),
         html.Th("Percent Difference"),
         ]))
]

row1 = html.Tr([
    html.Td("Characteristic Impedance (Ohms)"),
    html.Td("", id=f"calc-z0-{scenario.name}"),
    html.Td("", id=f"sim-z0-{scenario.name}"),
    html.Td("", id=f"z0-perc-diff-{scenario.name}")
])

table_body = [html.Tbody([row1, ])]

table = dbc.Table(table_header + table_body,
                  bordered=True,
                  dark=False,
                  hover=True,
                  responsive=False,
                  striped=True,
                  )


# %% Dash app layout
content = html.Div(children=[
    dbc.Row(
        [
            dbc.Col(
                dbc.Row(
                    [
                        sim_card,
                        form_card
                    ]
                ),
                width=5),
            dbc.Col(
                dbc.Row(
                    [
                        carousel,
                        table,
                    ]
                ),
                width=7),
        ],
    )], style=content_style)


# %% Callbacks
@app.long_callback(
    Output(component_id=f'sim-state-{scenario.name}',
           component_property='children'),
    Output(f'carousel-{scenario.name}', "items"),
    Output(f'sim-z0-{scenario.name}', "children"),
    Input(f'simulate-{scenario.name}-button', 'n_clicks'),
    State(f'width-input-{scenario.name}', 'value'),
    State(f'height-input-{scenario.name}', 'value'),
    State(f'dy-input-{scenario.name}', 'value'),
    State(f'er-input-{scenario.name}', 'value'),
    State(f'dx-input-{scenario.name}', 'value'),
    running=[
        (Output(f"calc-{scenario.name}-button", "disabled"), True, False),
        (
            Output(f"sim-state-{scenario.name}", "style"),
            {"visibility": "hidden"},
            {"visibility": "visible"},
        ),
        (
            Output(f"sim-progress-bar-{scenario.name}", "style"),
            {"visibility": "visible"},
            {"visibility": "hidden"},
        ),
    ],
    progress=[Output(f"sim-progress-bar-{scenario.name}", "value"),
              Output(f"sim-progress-bar-{scenario.name}", "max")],
    prevent_initial_call=True,
    interval=300
)
def run_sim(set_progress, sim_nclicks, width, height, dy, Er, dx):
    """Run FDA simulation and update table and carousel Dash elements."""
    if sim_nclicks == 0:
        return "Simulation not run!", [diagram_dict], ""
    if width and height and dy and Er and dx:
        scenario.trace_w = width*1e-3
        scenario.sub_thk = height*1e-3
        scenario.dy = dy*1e-3
        scenario.Er = Er
        scenario.dx = dx*1e-3
        root = get_project_root()
        filepath = root / 'src/webapp/assets/img/fda/scenarios'
        _, _, sim_z0 = scenario.run_sim(filepath=filepath,
                                        set_progress=set_progress)
    else:
        raise Exception("Invalid input.")
    sim_z0_str = str(round(sim_z0, 2))
    carousel_items = get_carousel_images()
    for x in carousel_items:
        print(x)
    return "Simulation complete!", carousel_items, sim_z0_str


@app.callback(
    Output(f'calc-z0-{scenario.name}', "children"),
    Output(f'z0-perc-diff-{scenario.name}', "children"),
    Input(f'calc-{scenario.name}-button', 'n_clicks'),
    Input(f'sim-z0-{scenario.name}', 'children'),
    State(f'width-input-{scenario.name}', 'value'),
    State(f'height-input-{scenario.name}', 'value'),
    State(f'dy-input-{scenario.name}', 'value'),
    State(f'er-input-{scenario.name}', 'value'),
    State(f'dx-input-{scenario.name}', 'value'),
    prevent_initial_call=True,

)
def analytical_calc(_, sim_z0, width, height, dy, Er, dx):
    """Display impedance calculated using analytical formula."""
    input_triggered = ctx.triggered_id
    calc_perc_diff = False
    if input_triggered == f"sim-z0-{scenario.name}":
        calc_perc_diff = True
    if width and height and dy and Er and dx:
        scenario.trace_w = width*1e-3
        scenario.sub_thk = height*1e-3
        scenario.dy = dy*1e-3
        scenario.Er = Er
        scenario.dx = dx*1e-3
        calc_z0 = scenario.analytical_soln()
    else:
        calc_z0 = "Invalid input"
        perc_diff = ""
        return calc_z0, perc_diff
    if sim_z0 and calc_perc_diff:
        sim_z0_float = float(sim_z0)
        perc_diff = (sim_z0_float - calc_z0) / sim_z0_float * 100
        perc_diff = str(round(perc_diff, 1))
        calc_z0 = str(round(calc_z0, 2))
        return calc_z0, perc_diff
    else:
        perc_diff = ""
        calc_z0 = str(round(calc_z0, 2))
        return calc_z0, perc_diff


def get_carousel_images():
    """Return list of dicts containing image paths for carousel."""
    root = get_project_root()
    path = root / f'src/webapp/assets/img/fda/scenarios/{scenario.name}'
    img_list = list_files(path)
    img_paths = []
    headers = []
    for img in img_list:
        headers.append(img.stem)
        parts = img.parts
        idx = parts.index('assets')
        reduced_path = parts[idx:]
        img_paths.append('/'.join(reduced_path))
    carousel_items = [
        {"key": f"{idx+1}", "src": img, "header": header}
        for idx, (img, header) in enumerate(zip(img_paths, headers))]
    carousel_items.append({
        "key": f"{len(carousel_items)+1}",
        "src": app.get_asset_url(f"img/fda/diagrams/{scenario.name}.png")})
    return carousel_items
