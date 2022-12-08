import pathlib
import pandas as pd
import dash
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from templates.ui_templates import get_slider_range, widget_card_chart, widget_card_chart_no_callback, get_radio_buttons
from templates.header_templates import get_theses_row_widgets_header
import helpers.functions as fn
import plotly.express as px
import sqlalchemy as sqla
import dash_dvx as dvx
import json
from math import log
import config

dash.register_page(__name__, path='/dashboard-theses')

#config params
theses_last_obs_date = config.THESES_LAST_OBS_DATE
theses_last_obs_date_text = config.THESES_LAST_OBS_DATE_TEXT
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
        f'select accessible_normalized, cas, embargo, embargo_duree, has_exist_embargo, annee_civile_soutenance, ecoles_doctorales_0_nom, oai_set_specs_0_regroup_label, oai_set_specs_0_main_domain from bso_theses_uca_{theses_last_obs_date} where annee_civile_soutenance < 2022', dbEngine)
    return df

def get_fr_data():
    df = pd.read_sql(
        f'select accessible_normalized, cas, embargo,has_exist_embargo, annee_civile_soutenance, oai_set_specs_0_regroup_label, oai_set_specs_0_main_domain from bso_theses_fr_{theses_last_obs_date} where annee_civile_soutenance > 2012 and annee_civile_soutenance < 2022', dbEngine)
    return df

df_uca = get_uca_data()
df_fr = get_fr_data()

# figs without callback
fig_has_embargo_rate_uca = px.pie(df_uca, names='has_exist_embargo', hole=0.7, color="has_exist_embargo", color_discrete_map= colors)
fig_has_embargo_rate_fr = px.pie(df_fr, names='has_exist_embargo', hole=0.7, color="has_exist_embargo", color_discrete_map= colors)

widgets_with_comment_dict = {
    "accessible-rate":f"Ces graphiques montrent les pourcentages de thèses de doctorat UCA (à gauche) et françaises (à droite) librement accessibles sur internet mesuré le {theses_last_obs_date_text} (date du dernier dump de données disponible sur data.gouv.fr). Ils montrent donc la proportion de thèses en accès libre versus les thèses accessibles uniquement en intranet car soumises à un embargo.",
    "has-embargo-rate": "Ces graphiques présentent, pour toutes les thèses de doctorat UCA (à gauche) et françaises (à doite) soutenues sur la période, les pourcentages de celles étant ou ayant été soumises à une période d'embargo retardant ou ayant retardé leur diffusion an accès libre pour tous.",
    "accessible-rate-by-year":f"Ce graphique détaille, en valeur absolue et en pourcentage, les proportions de thèses librement accessibles en fonction des années de soutenance à la date du {theses_last_obs_date_text} (date du dernier dump de données disponible sur data.gouv.fr)",
    "disc-repartition":f"Ce graphique montre la ventilation en numéraire et par discipline des thèses de doctorat UCA soutenues entre 2013 et 2021 (observées le {theses_last_obs_date_text}"
}

datatype_options = [
                    {"label": "Valeur absolue", "value": "qte"},
                    {"label": "Pourcentage", "value": "percent"},
]
                
indicatortype_options=[
                    {"label": "Moyenne", "value": "mean"},
                    {"label": "Médiane", "value": "median"},
                ]
display_variabletype_options = [
                    {"label": "Ecoles doctorales", "value": "ecoles_doctorales_0_nom"},
                    {"label": "Disciplines", "value": "oai_set_specs_0_main_domain"},
                ] 

row_widgets_header = get_theses_row_widgets_header(df_uca)

row_alert_bar = dbc.Row(dbc.Alert("Le jeu de données visualisé provient du dump complet de l'application Theses.fr exposé en Open Data et actualisé par l'Abes sur la plateforme data.gouv.fr. A noter que les métadonnées relatives aux restrictions de diffusion portent uniquement sur les éventuels embargos et non sur les thèses confidentielles. La notion d'accès restreint exploitée ici est donc partielle et conduit à une sous-évaluation des thèses réellement non accessibles.", color="warning"),)

row_widgets = html.Div(
    [   # Accessible general rate
        dbc.Row(dbc.Col(get_slider_range('accessible-rate', theses_period),width=12), className="text-center"),
        dbc.Row(
            [
                dbc.Col(widget_card_chart("accessible_rate_uca", f"Pourcentage de thèses UCA en accès libre (observé le {theses_last_obs_date_text})",), width=6),
                dbc.Col(widget_card_chart("accessible_rate_fr", f"Comparatif : Pourcentage de thèses françaises en accès libre (observé le {theses_last_obs_date_text})"), width=6),
            ]
        ),
        dbc.Row(dbc.Col(dbc.CardFooter(widgets_with_comment_dict["accessible-rate"]),width=12)),
        html.Hr(),
        # Accessible rate by year
        dbc.Row(dbc.Col(get_radio_buttons("accessible-rate", "Type de données :", datatype_options),width=12), className="text-center"),
        dbc.Row([
            dbc.Col(widget_card_chart("accessible_rate_by_year_uca","Thèses UCA en accès libre par année de soutenance"), width=6),
            dbc.Col(widget_card_chart("accessible_rate_by_year_fr","COMPARATIF : Thèses françaises en accès libre par année de soutenance"), width=6),
        ]),
        dbc.Row(dbc.Col(dbc.CardFooter(widgets_with_comment_dict["accessible-rate-by-year"]),width=12)),
        html.Hr(),
         # Has exists embargo
         dbc.Row(
            [
                dbc.Col(widget_card_chart_no_callback("has_embargo_rate_uca", fig_has_embargo_rate_uca, f"Pourcentage de thèses UCA étant soumises ou ayant été soumises à une période d'embargo",), width=6),
                dbc.Col(widget_card_chart_no_callback("has_embargo_rate_fr", fig_has_embargo_rate_fr, f"Comparatif : Pourcentage de thèses françaises étant soumises ou ayant été soumises à une période d'embargo"), width=6),
            ]
        ),
        dbc.Row(dbc.Col(dbc.CardFooter(widgets_with_comment_dict["has-embargo-rate"]),width=12)),
        html.Hr(),
        # embargo time by écoles doctorales or disc
        dbc.Row([dbc.Col(get_radio_buttons("embargo-time-ind", "Indicateur :", indicatortype_options),width=6),
                 dbc.Col(get_radio_buttons("embargo-time-var", "Comparer par :", display_variabletype_options),width=6)], 
                 className="text-center"),
        dbc.Row(dbc.Col(widget_card_chart("embargo_time_uca","Thèses UCA : nombres moyen et médian de jours d'embargo prévus par année de soutenance et école doctorale/discipline"),width=12)),
        html.Hr(),
        # analyse par disciplines
        dbc.Row(dbc.Col(get_slider_range('disc-repartition', theses_period),width=12), className="text-center"),
        dbc.Row(
            [
                dbc.Col(widget_card_chart("disc_repartition_uca", "Répartition des thèses UCA par discipline (Dewey) et ventilation par type d'accès (thèses étant ou ayant été sous embargo vs thèses en accès libre sans resrictions"), width=6),
                dbc.Col(widget_card_chart("disc_repartition_fr", "Répartition des thèses françaises par discipline (Dewey) et ventilation par type d'accès (thèses étant ou ayant été sous embargo vs thèses en accès libre sans resrictions"), width=6),
            ]
        ),
    ])

layout = [row_widgets_header,
          html.Hr(className="my-2"),
          row_alert_bar,
          #html.Hr(className="my-2"),
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
    Input("accessible-rate-radio-buttons","value"),
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
    Input("accessible-rate-radio-buttons","value"),
)
def update_accessible_rate_by_year_fr(radio_buttons):
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

@callback(
    Output('fig_embargo_time_uca', 'figure'),
    [Input("embargo-time-ind-radio-buttons","value"),
    Input("embargo-time-var-radio-buttons","value"),]
)
def update_embargo_time(radio_buttons_ind, radio_buttons_var):
    # Step: Change data type of annee_civile_soutenance to String/Text
    df_uca['annee_civile_soutenance'] = df_uca['annee_civile_soutenance'].astype('string')
    # Step: Change data type of embargo_duree to Integer
    df_uca['embargo_duree'] = pd.to_numeric(df_uca['embargo_duree'], downcast='integer', errors='coerce')
    data = pd.pivot_table(df_uca, columns=[f"{radio_buttons_var}"], index=['annee_civile_soutenance'], values='embargo_duree', aggfunc=f'{radio_buttons_ind}', fill_value=0)
    data = data.loc[(data != 0.0).any(axis=1)].reset_index()
    fig = px.line(data.sort_values(by=['annee_civile_soutenance'], ascending=[True]), x='annee_civile_soutenance', y=data.columns.tolist()[1:])
    fig.update_xaxes(title_text='Année de soutenance')
    fig.update_yaxes(title_text=f'Nombre de jours d\'embargo : {radio_buttons_ind}')
    fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
    ))
    return fig

## year range -> radar chart of disc for uca & fr
@callback(Output("fig_disc_repartition_uca", "figure"),
          Input("disc-repartition-year-range", "value"))
def update_disc_radar_uca(year_range):
    data = fn.get_filtered_data_by_year(df_uca, "annee_civile_soutenance", year_range)
    d = (pd.DataFrame(data[["oai_set_specs_0_regroup_label","has_exist_embargo"]].value_counts())
         .reset_index()
         .rename(columns={"oai_set_specs_0_regroup_label":"discipline","has_exist_embargo":"embargo",0:"count"})
         )
    d["log_count"] = d["count"].apply(lambda x: log(x,10))
    # Step: Sort column(s) oai_set_specs_0_regroup_label ascending (A-Z)
    d = d.sort_values(by=['discipline'], ascending=[True])
    fig = px.line_polar(d, r="log_count", theta="discipline", color="embargo", line_close=True,
                    color_discrete_map=colors,
                    template=plotly_template,)
    fig.update_traces(fill='tonext')
    return fig

# year range -> radar chart of disc
@callback(Output("fig_disc_repartition_fr", "figure"),
          Input("disc-repartition-year-range", "value"))
def update_disc_radar_uca(year_range):
    data = fn.get_filtered_data_by_year(df_fr, "annee_civile_soutenance", year_range)
    d = (pd.DataFrame(data[["oai_set_specs_0_regroup_label","has_exist_embargo"]].value_counts())
         .reset_index()
         .rename(columns={"oai_set_specs_0_regroup_label":"discipline","has_exist_embargo":"embargo",0:"count"})
         )
    d["log_count"] = d["count"].apply(lambda x: log(x,10))
    # Step: Sort column(s) oai_set_specs_0_regroup_label ascending (A-Z)
    d = d.sort_values(by=['discipline'], ascending=[True])
    fig = px.line_polar(d, r="log_count", theta="discipline", color="embargo", line_close=True,
                    color_discrete_map=colors,
                    template=plotly_template,)
    fig.update_traces(fill='tonext')
    return fig