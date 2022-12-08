import dash
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from templates.ui_templates import widget_card_header
import config

dash.register_page(__name__, path='/')

# config variables
url_subpath = config.URL_SUBPATH

left_jumbotron_old = dbc.Col(
    html.Div(
        [
            html.H2("Baromètre des publications", className="display-3"),
            html.Hr(className="my-2"),
            html.P(
                "Le baromètre UCA des publications mesure l’évolution de la pratique d’ouverture des publications des chercheurs et enseignants-chercheurs de l’Université Côte d'Azur depuis 2016. Il s’inspire de la méthodologie définie par le MESRI pour son baromètre national développé dans le cadre du Plan national pour la Science ouverte"
            ),
            html.P("Le périmètre actuel du baromètre Open Access UCA recouvre les publications depuis 2016 référencées dans Scopus disposant d'un DOI et ayant au moins un auteur avec au moins une affiliation UCA"),
            dbc.Row([
                dbc.Col(widget_card_header("nb_publis","Nombre de publications", text="14 607"), width={"offset": 1, "size":4}),
                dbc.Col(widget_card_header("oa_rate_total","Taux d'accès ouvert", text="68,2 %"), width=4),
                ]),
            html.Hr(className="my-2"),
            dbc.Button("Accéder", color="light", outline=True),
        ],
        className="h-100 p-5 text-white bg-dark rounded-3",
    ),
    md=6,
)

left_jumbotron = dbc.Col(
    html.Div(
        [
            html.H2("Baromètre des publications"),
            html.Hr(className="my-2"),
            html.P(
                "Le baromètre UCA des publications mesure l’évolution de la pratique d’ouverture des publications des chercheurs et enseignants-chercheurs de l’Université Côte d'Azur depuis 2016. Il s’inspire de la méthodologie définie par le MESRI pour son baromètre national développé dans le cadre du Plan national pour la Science ouverte"
            ),
            html.P("Le périmètre actuel du baromètre Open Access UCA recouvre les publications depuis 2016 référencées dans Scopus disposant d'un DOI et ayant au moins un auteur avec au moins une affiliation UCA"),
            dbc.Row([
                dbc.Col(widget_card_header("nb_publis","Nombre de publications", text="14 607"), width={"offset": 1, "size":5}),
                dbc.Col(widget_card_header("oa_rate_total","Taux d'accès ouvert", text="68,2 %"), width=5),
                ]),
            #html.Hr(className="my-2"),
            html.P(dbc.Button("Accéder", color="secondary", outline=True, href=f"{url_subpath}dashboard-publications"),className="lead text-center mt-5")
        ],
        className="h-100 p-5 bg-light border rounded-3",
    ),
    md=6,
)

right_jumbotron = dbc.Col(
    html.Div(
        [
            html.H2("Baromètre des thèses"),
            html.Hr(className="my-2"),
            html.P(
                "Le baromètre UCA des thèses présente un état des lieux des modalités de diffusion des thèses de doctorat délivrées par Université Côte d'Azur (et anciennement l'Université de Nice Sophia Antipolis) et déposées en format électronique depuis 2013"
            ),
            html.P("Il se base sur les métadonnées descriptives de Thèses.fr exposées en Open Data sur data.gouv.fr par l'Abes"),
            dbc.Row([
                dbc.Col(widget_card_header("nb_theses","Nombre de thèses", text="2 107"),width={"offset": 1, "size":5}),
                dbc.Col(widget_card_header("theses_oa_rate_total","Taux d'ouverture", text="64.7 %"), width=5),
                ],
                className="mt-5"),
            #html.Hr(className="my-2"),
            html.P(dbc.Button("Accéder", color="secondary", outline=True,  href=f"{url_subpath}dashboard-theses"),className="lead text-center mt-5")
        ],
        className="h-100 p-5 bg-light border rounded-3",
    ),
    md=6,
)
layout = dbc.Row(
    [left_jumbotron, right_jumbotron],
    className="align-items-md-stretch",
)