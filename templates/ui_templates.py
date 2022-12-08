import dash
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
import dash_loading_spinners as dls


def load_with_spinner(composant):
    return dls.Hash(composant,
                        color="#435278",
                        speed_multiplier=2,
                        size=70,)

def widget_card_header(id, title, text=None):
    if text is not None:
        div_section = html.Div(id=f'{id}', children=[text])
    else:
        div_section = html.Div(id=f'{id}')
    card = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.P(f"{title}", className="card-title"),
                    html.Hr(className="my-2"),
                    html.H5(
                        div_section,
                        className="card-text text-center ",
                    ),
                ]
            ),
        ],
        color="rgb(113, 145, 179)",
        outline=True,
        inverse=True,
        #style={"width": "12rem"},
    )
    return card


def widget_card_chart(id, title, bsonat_iframe_src=None, slider_range=None, radio_buttons=None, select_publisher=None, comment=None):
    if bsonat_iframe_src is not None:
        bsonat_section = html.Div([
            dbc.Button("Voir les données du baromètre national",
                       id=f"bsonat_open_{id}", outline=True, color="primary", size="sm", n_clicks=0),
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle("Baromètre national"), close_button=True
                    ),
                    dbc.ModalBody(
                        html.Iframe(src=bsonat_iframe_src, style={
                                    "height": "800px", "width": "100%"})
                    ),
                    dbc.ModalFooter(dbc.Button(
                        "Fermer", id=f"bsonat_close_{id}", className="btn bg-gradient-dark ml-auto", n_clicks=0))
                ],
                id=f"bsonat_modal_{id}",
                centered=True,
                size="lg",
                keyboard=True,
                backdrop="static",
                is_open=False
            )
        ],
            className="col text-end")
    else:
        bsonat_section = html.Div()
    if slider_range is not None:
        slider_range_section = slider_range
    else:
        slider_range_section = html.Div()
    if radio_buttons is not None:
        radio_buttons_section = radio_buttons
    else:
        radio_buttons_section = html.Div()
    if select_publisher is not None:
        select_publisher_section = select_publisher
    else:
        select_publisher_section = html.Div()
    if comment is not None:
        comment_div = dbc.CardFooter(f"{comment}")
    else:
        comment_div = html.Div()
    card = dbc.Card([
        dbc.CardHeader([dbc.Row(
                    [
                        dbc.Col(
                            html.H2(f"{title}", className="fs-5 fw-bold mb-3"), width=8),
                        dbc.Col(bsonat_section, width=4)
                    ]
                    ),
            dbc.Row(
            [dbc.Col(slider_range_section, width=12)]
        ),
            dbc.Row(
            [dbc.Col(radio_buttons_section, width=12)]
        ),
            dbc.Row(
            [dbc.Col(select_publisher_section, width=12)]
        )
        ]),
        dbc.CardBody(
            [
                load_with_spinner(dcc.Graph(id=f"fig_{id}"))
            ],
        ),
        comment_div
    ],color="light", outline=True)
    return card


def widget_card_chart_no_callback(id, fig, title, bsonat_iframe_src=None, comment=None):
    if bsonat_iframe_src is not None:
        bsonat_section = html.Div([
            dbc.Button("Voir les données du baromètre national",
                       id=f"bsonat_open_{id}", outline=True, color="primary", size="sm", n_clicks=0),
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle("Baromètre national"), close_button=True
                    ),
                    dbc.ModalBody(
                        html.Iframe(src=bsonat_iframe_src, style={
                                    "height": "800px", "width": "100%"})
                    ),
                    dbc.ModalFooter(dbc.Button(
                        "Fermer", id=f"bsonat_close_{id}", className="btn bg-gradient-dark ml-auto", n_clicks=0))
                ],
                id=f"bsonat_modal_{id}",
                centered=True,
                size="lg",
                keyboard=True,
                backdrop="static",
                is_open=False
            )
        ],
            className="col text-end")
    else:
        bsonat_section = html.Div()
    if comment is not None:
        comment_div = dbc.CardFooter(f"{comment}")
    else:
        comment_div = html.Div()
    card = dbc.Card([
        dbc.CardHeader(dbc.Row(
                    [
                        dbc.Col(html.H2(f"{title}",
                                        className="fs-5 fw-bold mb-0"), width=8),
                        dbc.Col(bsonat_section, width=4)
                    ]
                    )
        ),
        dbc.CardBody(
            [
                load_with_spinner(dcc.Graph(figure=fig))
            ]
        ),
         comment_div
    ], color="light", outline=True)
    return card

def get_slider_range(div_id,period):
    # markers
    period_marks = {}
    keys = range(period[0], period[1], 1)
    for i in keys:
        period_marks[i] = str(i)
    # slider
    return html.Div(dbc.Row([
        dbc.Col(dbc.Label("Filtrer par année de publication", className="fst-bold"),width=4),
        dbc.Col(dcc.RangeSlider(period[0], period[1] - 1, 1, value=[
            period[0], period[1] - 1], marks=period_marks, id=f'{div_id}-year-range'), width=8)
    ],
    className="fst-italic fw-bold bg-opacity-25 p-2 m-1 bg-primary text-light border rounded-pill")
    )

def get_radio_buttons(div_id,label,options):
    return html.Div(
        dbc.Row([
            dbc.Col(dbc.Label(f"{label}"), width=3),
            dbc.Col(dbc.RadioItems(
                options=options,
                inline=True,
                value=options[0]["value"],
                id=f"{div_id}-radio-buttons"
            ), width=9)
        ],
        className="fst-italic fw-bold bg-opacity-25 p-2 m-1 bg-primary text-light border rounded-pill")
    )

def get_select_publisher(div_id,dict_publishers):
    return html.Div(dcc.Dropdown(
       id=f"{div_id}-selected_publisher",
       options=dict_publishers,
       multi=False,
       value=dict_publishers[0]['value']
    ),
     className="fst-italic fw-bold bg-opacity-25 p-2 m-1 bg-primary text-light border rounded-pill") 

# [Unused]
# example : dbc.Col(widget_card_chart("oa_and_hosttype","Répartition des publications par voie d'ouverture",bsonat_iframe_src=widgets_with_iframe_dict['oa_and_hosttype'], radio_buttons=get_radio_buttons_date_obs_vs_all_dataset("oa-and-hosttype", publis_last_obs_date[:4])), width=6),
def get_radio_buttons_date_obs_vs_all_dataset(div_id, date_obs):
    return html.Div(dbc.Row([
        dbc.Col(dbc.Label("Périmètre"), width=2),
        dbc.Col(dbc.RadioItems(
            options=[
                {"label": f"Tout le dataset observé en {date_obs}", "value": "all"},
                {"label": f"Seulement les publications parues en {int(date_obs) -1} observées en {date_obs}",
                    "value": "previous"},
            ],
            inline=True,
            value="all",
            id=f"{div_id}-radio-date-obs-vs-all-dataset"
        ), width=10)],
        className="fst-italic fw-bold bg-opacity-25 p-2 m-1 bg-primary text-light border rounded-pill")
    )

# [Unused]
# example :  dbc.Col([widget_card_chart("oa_rate","Taux d'accès ouvert global",slider_range=get_slider_range("oa-rate"), collapse_div=get_collapse_comment("oa-rate",widgets_with_collapse_dict["oa-rate"]))], width=4),
"""for key in widgets_with_collapse_dict:
    @callback(
    Output(f"collapse-output-{key}", "is_open"),
    [Input(f"collapse-open-{key}", "n_clicks")],
    [State(f"collapse-output-{key}", "is_open")],
    )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open"""
def get_collapse_comment(div_id, output):
    return html.Div(
        [
            dbc.Button(
                "Commentaire",
                id=f"collapse-open-{div_id}",
                className="mb-3",
                color="link",
                n_clicks=0,
            ),
            dbc.Collapse(
                html.P(output),
                id=f"collapse-output-{div_id}",
                is_open=False,
            ),
        ])
