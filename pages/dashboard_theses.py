import pathlib
import pandas as pd
import dash
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from templates.ui_templates import get_slider_range, widget_card_header, widget_card_chart, widget_card_chart_no_callback, get_radio_buttons_datatype
from templates.header_templates import get_theses_row_widgets_header
import helpers.functions as fn
import plotly.express as px
import sqlalchemy as sqla
import dash_dvx as dvx
import json
import config

dash.register_page(__name__, path='/dashboard-theses')

#config params
theses_last_obs_date = config.THESES_LAST_OBS_DATE
theses_obs_dates = config.THESES_OBS_DATES
theses_period = config.THESES_PERIOD
colors = config.COLORS
plotly_template = config.PLOTLY_TEMPLATE

# get relative db folder
PATH = pathlib.Path(__file__).parent
DB_PATH = PATH.joinpath("../db", "theses.db").resolve()

dbEngine=sqla.create_engine(f'sqlite:///{DB_PATH}')

def get_uca_data():
    df = pd.read_sql(
        f'select accessible_normalized, cas, embargo, has_exist_embargo, annee_civile_soutenance, ecoles_doctorales_0_nom, oai_set_specs_0_label, oai_set_specs_0_main_domain from bso_theses_uca_{theses_last_obs_date} where annee_civile_soutenance < 2022', dbEngine)
    return df

def get_fr_data():
    df = pd.read_sql(
        f'select accessible_normalized, cas, embargo, has_exist_embargo, annee_civile_soutenance, oai_set_specs_0_label, oai_set_specs_0_main_domain from bso_theses_fr_{theses_last_obs_date} where annee_civile_soutenance > 2012 and annee_civile_soutenance < 2022', dbEngine)
    return df

df_uca = get_uca_data()
df_fr = get_fr_data()

widgets_with_comment_dict = {
    "accessible-rate-uca":"Ce graphique montre le pourcentage de thèses de doctorat Université Côte d'Azur librement accessibles sur internet mesuré le 17 octobre 2022 (date du dernier dump de données disponible sur data.gouv.fr)",
    "accessible-rate-by-year":"Ce graphique détaille, en valeur absolue et en pourcentage, les proportions de thèses librement accessibles en fonction des années de soutenance, et mesurées le 17 octobre 2022 (date du dernier dump de données disponible sur data.gouv.fr)"
}

row_widgets_header = get_theses_row_widgets_header(df_uca)

row_widgets = html.Div(
    [   dbc.Row(dbc.Col(get_slider_range('accessible-rate', theses_period),width=12)),
        dbc.Row(
            [
                dbc.Col(widget_card_chart("accessible_rate_uca", "Pourcentage de thèses UCA en accès libre",
                        comment = widgets_with_comment_dict["accessible-rate-uca"]), width=6),
                dbc.Col(widget_card_chart("accessible_rate_fr", "Comparatif : Pourcentage de thèses françaises en accès libre"), width=6),
            ]
        ),
        html.Hr(),
        dbc.Row(dbc.Col(get_radio_buttons_datatype("accessible-rate"),width=12)),
        dbc.Row([
            dbc.Col(widget_card_chart("accessible_rate_by_year_uca","Thèses UCA en accès libre par année de soutenance",comment = widgets_with_comment_dict["accessible-rate-by-year"]), width=6),
            dbc.Col(widget_card_chart("accessible_rate_by_year_fr","COMPARATIF : Thèses françaises en accès libre par année de soutenance"), width=6),
        ])
    ])

layout = [row_widgets_header,
          html.Hr(className="my-2"),
          row_widgets]

########### CHARTS CALLBACKS ########################
#####################################################

## slider range -> pie charts uca + fr
@callback(
    [Output('fig_accessible_rate_uca', 'figure'),
    Output('fig_accessible_rate_fr', 'figure')],
    Input("accessible-rate-year-range","value"),
)
def update_accessible_rate(year_range):
    data_uca = fn.get_filtered_data_by_year(df_uca,"annee_civile_soutenance",year_range)
    data_fr = fn.get_filtered_data_by_year(df_fr,"annee_civile_soutenance",year_range)
    fig_uca = px.pie(data_uca, names='accessible_normalized', hole=0.7, color="accessible_normalized", color_discrete_map= colors)
    fig_fr = px.pie(data_fr, names='accessible_normalized', hole=0.7, color="accessible_normalized", color_discrete_map= colors)
    return fig_uca, fig_fr

## UCA radio button data type % or absolute -> vertical barchart access by year
@callback(
    Output('fig_accessible_rate_by_year_uca', 'figure'),
    Input("accessible-rate-radio-detail-datatype","value"),
)
def update_accessible_rate_by_year_uca(radio_buttons):
    crosstab_df = fn.get_crosstab_simple(df_uca, "annee_civile_soutenance", "accessible_normalized")
    crosstab_percent_df = fn.get_crosstab_percent(df_uca, "annee_civile_soutenance", "accessible_normalized")
    if radio_buttons == "qte":
        fig = px.bar(crosstab_df, x='annee_civile_soutenance',
                     y=["Accès libre", "Accès restreint"], color_discrete_map=colors, template=plotly_template)
        fig.update_yaxes(title_text='Nombre de thèses')
        fig.update_traces(textposition='inside',texttemplate = "%{value}")
    if radio_buttons == "percent":
        fig = px.bar(crosstab_percent_df, x='annee_civile_soutenance',
                     y=["Accès libre", "Accès restreint"], color_discrete_map=colors, template=plotly_template)
        fig.update_yaxes(title_text='Taux d\'ouverture')
        fig.update_traces(textposition='inside',texttemplate = "%{value}"+"%")
    fig.update_xaxes(title_text='Année de soutenance')
    fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
    ),
    margin=dict(l=10, r=10, t=10, b=10))
    return fig

## FR radio button data type % or absolute -> vertical barchart access by year
@callback(
    Output('fig_accessible_rate_by_year_fr', 'figure'),
    Input("accessible-rate-radio-detail-datatype","value"),
)
def update_accessible_rate_by_year_uca(radio_buttons):
    crosstab_df = fn.get_crosstab_simple(df_fr, "annee_civile_soutenance", "accessible_normalized")
    crosstab_percent_df = fn.get_crosstab_percent(df_fr, "annee_civile_soutenance", "accessible_normalized")
    if radio_buttons == "qte":
        fig = px.bar(crosstab_df, x='annee_civile_soutenance',
                     y=["Accès libre", "Accès restreint"], color_discrete_map=colors, template=plotly_template)
        fig.update_yaxes(title_text='Nombre de thèses')
        fig.update_traces(textposition='inside',texttemplate = "%{value}")
    if radio_buttons == "percent":
        fig = px.bar(crosstab_percent_df, x='annee_civile_soutenance',
                     y=["Accès libre", "Accès restreint"], color_discrete_map=colors, template=plotly_template)
        fig.update_yaxes(title_text='Taux d\'ouverture')
        fig.update_traces(textposition='inside',texttemplate = "%{value}"+"%")
    fig.update_xaxes(title_text='Année de soutenance')
    fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
    ),
    margin=dict(l=10, r=10, t=10, b=10))
    return fig