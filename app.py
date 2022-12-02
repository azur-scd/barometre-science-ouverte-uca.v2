import dash
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
import config

# config variables
port = config.PORT
host = config.HOST
url_subpath = config.URL_SUBPATH

# external JavaScript f& CSS iles
external_scripts = [
    'https://cdnjs.cloudflare.com/ajax/libs/devextreme/22.1.3/js/dx.all.js',
]

# external CSS stylesheets
external_stylesheets = [
    dbc.themes.LUX,
    'https://cdnjs.cloudflare.com/ajax/libs/devextreme/22.1.3/css/dx.material.blue.light.compact.css',
]

app = dash.Dash(
    __name__, use_pages=True, suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width"}],
    external_scripts=external_scripts,
    external_stylesheets=external_stylesheets,
    url_base_pathname=url_subpath
)
#app.config.suppress_callback_exceptions = True

app.title = "BSO UCA"
server = app.server

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=app.get_asset_url(
                            'logo_UCA_bibliotheque_ligne_couleurs.png'), height="40px")),
                        dbc.Col(dbc.NavbarBrand(
                            "Barometre Science Ouverte UCA", className="ms-2")),
                    ],
                    align="center",
                    className="g-0",
                ),
                href=f"{url_subpath}",
                style={"textDecoration": "none"},
            ),
            dbc.Collapse(
                dbc.Nav(
                    [dbc.NavItem(dbc.NavLink("Home", href=f"{url_subpath}")),
                     dbc.DropdownMenu(
                        children=[
                            dbc.DropdownMenuItem("Baromètre général",
                                                 href=f"{url_subpath}dashboard-publications"),
                            dbc.DropdownMenuItem(
                                "Disciplines", href=f"{url_subpath}dashboard-publications-diciplines"),
                            dbc.DropdownMenuItem("Editeurs", href=f"{url_subpath}dashboard-publications-editeurs"),
                            dbc.DropdownMenuItem(divider=True),
                            dbc.DropdownMenuItem(
                                "Données", href=f"{url_subpath}data-publications"),
                            dbc.DropdownMenuItem(
                                "Référentiel des strutures", href=f"{url_subpath}referentiel-structures"),
                        ],
                        nav=True,
                        in_navbar=True,
                        label="Publications",
                    ),
                        dbc.DropdownMenu(
                        children=[
                            dbc.DropdownMenuItem(
                                "Baromètre général", href=f"{url_subpath}dashboard-theses"),
                            dbc.DropdownMenuItem("Disciplines", href=f"{url_subpath}"),
                            dbc.DropdownMenuItem(
                                "Ecoles doctorales", href=f"{url_subpath}"),
                            dbc.DropdownMenuItem(divider=True),
                            dbc.DropdownMenuItem("Données", href=f"{url_subpath}"),
                        ],
                        nav=True,
                        in_navbar=True,
                        label="Thèses",
                    )],
                    className="ms-auto",
                    navbar=True,
                ),
                id="navbar-collapse2",
                navbar=True,
            ),
        ],
        style={"max-width": "1800px"}
    ),
    color="#7191b3",
    dark=True,
    className="mb-5",
)

footer = html.Div(
    [
        html.Footer(
            [
                html.Div(
                    [
                        html.Span(
                            "2022 - SCD Université Côte d'Azur. | Contact : "),
                        dcc.Link(html.A('geraldine.geoffroy@univ-cotedazur.fr'),
                                 href="mailto:geraldine.geoffroy@univ-cotedazur.fr")
                    ])
            ]
        )
    ],
    id="footer",
    className="text-center",
    style={"margin-bottom": "25px"}
)

app.layout = dbc.Container(
    fluid=True,
    children=[
        navbar,
        dash.page_container,
        html.Hr(),
        footer
    ],
)

# Main
if __name__ == "__main__":
    app.run_server(debug=True, port=port, host=host)
