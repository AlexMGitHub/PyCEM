"""Page for differential stripline FDA simulation."""
# %% Imports
# Standard system imports

# Related third party imports
from dash import html, Input, Output, State, ctx
import dash_bootstrap_components as dbc

# Local application/library specific imports
from webapp.app import app
from webapp.pages.styling import content_style
from pycem.fda_scenarios import DifferentialStripline
from pycem.utilities import get_project_root, list_files


# %% Globals
scenario = DifferentialStripline()


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

spacing_input = html.Div(
    [
        dbc.Label("Spacing (S)", html_for=f"spacing-input-{scenario.name}"),
        dbc.Input(
            type="number",
            id=f"spacing-input-{scenario.name}",
            min=0,
            step=0.001,
            value=0.2
        ),
        dbc.FormText(
            "Enter the spacing between the two traces in millimeters.",
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

form = dbc.Form([width_input, height_input, dy_input, spacing_input, er_input,
                 dx_input])

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
    html.Td("Differential Impedance (Ohms)"),
    html.Td("", id=f"calc-diff-{scenario.name}"),
    html.Td("", id=f"sim-diff-{scenario.name}"),
    html.Td("", id=f"diff-perc-diff-{scenario.name}")
])

row2 = html.Tr([
    html.Td("Common Impedance (Ohms)"),
    html.Td("", id=f"calc-comm-{scenario.name}"),
    html.Td("", id=f"sim-comm-{scenario.name}"),
    html.Td("", id=f"comm-perc-diff-{scenario.name}")
])

table_body = [html.Tbody([row1, row2])]

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
    Output(f'sim-diff-{scenario.name}', "children"),
    Output(f'sim-comm-{scenario.name}', "children"),
    Input(f'simulate-{scenario.name}-button', 'n_clicks'),
    State(f'width-input-{scenario.name}', 'value'),
    State(f'height-input-{scenario.name}', 'value'),
    State(f'dy-input-{scenario.name}', 'value'),
    State(f'spacing-input-{scenario.name}', 'value'),
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
def run_sim(set_progress, sim_nclicks, width, height, dy, spacing, Er, dx):
    """Run FDA simulation and update table and carousel Dash elements."""
    if sim_nclicks == 0:
        return "Simulation not run!", [diagram_dict], "", ""
    if width and height and dy and spacing and Er and dx:
        scenario.trace_w = width*1e-3
        scenario.sub_thk = height*1e-3
        scenario.dy = dy*1e-3
        scenario.spacing = spacing*1e-3
        scenario.Er = Er
        scenario.dx = dx*1e-3
        root = get_project_root()
        filepath = root / 'src/webapp/assets/img/fda/scenarios'
        (_, _, diff_z0, _, _, comm_z0, _, _) = scenario.run_sim(
            filepath=filepath,
            set_progress=set_progress)
    else:
        raise Exception("Invalid input.")
    diff_z0_str = str(round(diff_z0, 2))
    comm_z0_str = str(round(comm_z0, 2))
    carousel_items = get_carousel_images()
    for x in carousel_items:
        print(x)
    return "Simulation complete!", carousel_items, diff_z0_str, comm_z0_str


@app.callback(
    Output(f'calc-diff-{scenario.name}', "children"),
    Output(f'diff-perc-diff-{scenario.name}', "children"),
    Output(f'calc-comm-{scenario.name}', "children"),
    Output(f'comm-perc-diff-{scenario.name}', "children"),
    Input(f'calc-{scenario.name}-button', 'n_clicks'),
    Input(f'sim-diff-{scenario.name}', 'children'),
    State(f'sim-comm-{scenario.name}', 'children'),
    State(f'width-input-{scenario.name}', 'value'),
    State(f'height-input-{scenario.name}', 'value'),
    State(f'dy-input-{scenario.name}', 'value'),
    State(f'spacing-input-{scenario.name}', 'value'),
    State(f'er-input-{scenario.name}', 'value'),
    State(f'dx-input-{scenario.name}', 'value'),
    prevent_initial_call=True,

)
def analytical_calc(_, sim_diff, sim_comm, width, height, dy, spacing, Er, dx):
    """Display impedance calculated using analytical formula."""
    input_triggered = ctx.triggered_id
    calc_perc_diff = False
    if input_triggered == f"sim-diff-{scenario.name}":
        calc_perc_diff = True
    if width and height and dy and spacing and Er and dx:
        scenario.trace_w = width*1e-3
        scenario.sub_thk = height*1e-3
        scenario.dy = dy*1e-3
        scenario.spacing = spacing*1e-3
        scenario.Er = Er
        scenario.dx = dx*1e-3
        (diff_z0, comm_z0, _, _) = scenario.analytical_soln()
    else:
        calc_z0 = "Invalid input"
        perc_diff = ""
        return calc_z0, perc_diff, calc_z0, perc_diff
    if sim_diff and calc_perc_diff:
        sim_diff_float = float(sim_diff)
        sim_comm_float = float(sim_comm)
        diff_perc_diff = (sim_diff_float - diff_z0) / sim_diff_float * 100
        diff_perc_diff = str(round(diff_perc_diff, 1))
        comm_perc_diff = (sim_comm_float - comm_z0) / sim_comm_float * 100
        comm_perc_diff = str(round(comm_perc_diff, 1))
        diff_z0 = str(round(diff_z0, 2))
        comm_z0 = str(round(comm_z0, 2))
        return diff_z0, diff_perc_diff, comm_z0, comm_perc_diff
    else:
        perc_diff = ""
        diff_z0 = str(round(diff_z0, 2))
        comm_z0 = str(round(comm_z0, 2))
        return diff_z0, perc_diff, comm_z0, perc_diff


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
