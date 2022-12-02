import pathlib
import pandas as pd
import dash
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from templates.ui_templates import get_slider_range, widget_card_header, widget_card_chart, widget_card_chart_no_callback, get_radio_buttons_chart_order
from templates.header_templates import get_publis_row_widgets_header
import helpers.functions as fn
import plotly.express as px
import sqlalchemy as sqla
import json
import config

dash.register_page(__name__, path='/dashboard-publications-diciplines')

# config params
publis_last_obs_date = config.PUBLIS_LAST_OBS_DATE
publis_period = config.PUBLIS_PERIOD
colors = config.COLORS
plotly_template = config.PLOTLY_TEMPLATE

# For loop of callbacks on the bso modal url
widgets_with_iframe_dict = {"oa_rate_by_year_faceting_disc": "https://barometredelascienceouverte.esr.gouv.fr/integration/fr/publi.disciplines.dynamique-ouverture.chart-taux-ouverture",
                            "hosttype_by_disc": "https://barometredelascienceouverte.esr.gouv.fr/integration/fr/publi.disciplines.voies-ouverture.chart-repartition-publications",
                            "hosttype_disc_scatter": "https://barometredelascienceouverte.esr.gouv.fr/integration/fr/publi.disciplines.voies-ouverture.chart-evolution-comparaison-types-hebergement"
                            }
widgets_with_comment_dict = {"disc-repartition":"Ce graphique montre la ventilation en numéraire et par discipline des publications UCA parues entre 2016 et 2021 et observées en 2022, et illustre la part prépondérante, quelle que soit l'intervalle de date de publication considéré, des publications en Médecine",
                             "oa-rate-by-year-faceting-disc": "Cet ensemble de graphiques présentant les différents niveaux d'accès ouverts par date de publication et par discipline (observés en 2022) démontre les fortes diversités disciplinaires dans la mise en pratique de l'ouverture des publications, avec par exemple des champs disciplinaires traditionnellement et historiquement plus ancrés dans la pratique du libre accès aux résultats de la recherche (comme les mathématiques, les sciences phyqiues et les sciences de la terre), ou encore des dynamiques très différentes entre la chimie et l'informatique.",
                             "hosttype-by-disc": "Ce graphique illustre également, dans le détail des voies d'ouverture privilégiées par discipline, des caractéristiques disciplinaires très marquées, notamment concernant la systématisation (ou non) du dépôt des publications en archive ouverte.",
                             "hosttype-disc-scatter": "Dans ce graphique, chaque discipline est représentée par une bulle dont la taille est proportionnelle au volume des publications UCA observées en 2022. Le positionnement de la bulle dans l'espace est lié au pourcentage de publication accessible en open access depuis les plateformes éditeurs (en abscisse) et au pourcentage équivalent pour l'accès en OA via une archive ouverte (en ordonnée). Plus la bulle est située en haut à droite du graphique plus les publications sont ouvertes à la fois sur une archive ouverte et sur les sites éditeurs."
                             }
# get relative db folder
PATH = pathlib.Path(__file__).parent
DB_PATH = PATH.joinpath("../db", "publications.db").resolve()

dbEngine = sqla.create_engine(f'sqlite:///{DB_PATH}')


def get_data():
    df = pd.read_sql(
        f'select doi, year, is_oa_normalized, oa_host_type_normalized, bso_classification_fr from bso_publis_uniques_{publis_last_obs_date}', dbEngine)
    return df

def get_disc_count_data(limit=None):
    if limit is not None:
        df = pd.read_sql(
        f'SELECT bso_classification_fr, count(*) as count FROM bso_publis_uniques_{publis_last_obs_date}  GROUP BY bso_classification_fr ORDER BY count ASC LIMIT {limit}', dbEngine)
    else:
        df = pd.read_sql(
        f'SELECT bso_classification_fr, count(*) as count FROM bso_publis_uniques_{publis_last_obs_date} GROUP BY bso_classification_fr ORDER BY count ASC', dbEngine)
    return df

def get_hosttype_exploded_data():
    df = get_data()
    df['oa_host_type_normalized_tmp'] = df['oa_host_type_normalized'].apply(
        lambda x: ["Editeur", "Archive ouverte"] if (x == "Editeur et archive ouverte") else list(x.split(",")))
    data = df.assign(oa_host_type_normalized_explode=df['oa_host_type_normalized_tmp']).explode(
        'oa_host_type_normalized_explode').drop(columns=['oa_host_type_normalized_tmp', 'oa_host_type_normalized'])
    return data


df = get_data()
top10_disc_list = [s["bso_classification_fr"] for s in get_disc_count_data(limit=10).to_dict("records")]
# set of publis data -> horizontal barchart oa rate by year faceting disicplines
data = (df.groupby(['year', 'bso_classification_fr']).is_oa_normalized.value_counts(
    normalize=True).mul(100).round(1).rename('percent').reset_index(2))
data = data.reset_index()
data = data.loc[data['is_oa_normalized'].str.contains(
    'Accès ouvert', case=True, regex=False, na=False)]
fig_oa_rate_by_year_faceting_disc = px.bar(data, x='year', y='percent', facet_col='bso_classification_fr',
                                           facet_col_wrap=3, color_discrete_sequence=[colors['Accès ouvert']], height=1200, template=plotly_template)
#fig_oa_rate_by_year_faceting_disc.update_xaxes(title_text='Année de publication', showticklabels=True)
fig_oa_rate_by_year_faceting_disc.update_xaxes(showticklabels=True)
fig_oa_rate_by_year_faceting_disc.update_yaxes(title_text='Taux d\'ouverture')
fig_oa_rate_by_year_faceting_disc.update_xaxes(
    title_text='Année de publication')
fig_oa_rate_by_year_faceting_disc.update_traces(
    textposition='inside', texttemplate="%{value}"+"%")
fig_oa_rate_by_year_faceting_disc.for_each_annotation(
    lambda a: a.update(text=a.text.split("=")[-1].upper()))

row_widgets_header = get_publis_row_widgets_header(df)

row_widgets = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(widget_card_chart("disc_repartition", "Répartition des publications par discipline",
                        slider_range=get_slider_range('disc_repartition', publis_period), comment = widgets_with_comment_dict["disc-repartition"]), width=6),
                dbc.Col(dbc.Card(html.Div(
                    "Les disciplines représentées sont celles retenues dans le Baromètre Science ouverte national, elles-mêmes issues des classifications des bases CNRS Pascal et Faancis. Les champs disciplinaires de déclinent comme suit : ... en cours..."), body=True,), width=6)
            ]
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(widget_card_chart_no_callback('oa_rate_by_year_faceting_disc',fig_oa_rate_by_year_faceting_disc, "Evolution du taux d'accès ouvert par discipline et par date de publication",
                        bsonat_iframe_src=widgets_with_iframe_dict['oa_rate_by_year_faceting_disc'], comment = widgets_with_comment_dict["oa-rate-by-year-faceting-disc"]), width=12),
            ]
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(widget_card_chart("hosttype_by_disc", "Répartition des publications françaises par voie d'ouverture pour chaque discipline",
                        bsonat_iframe_src=widgets_with_iframe_dict['hosttype_by_disc'], slider_range=get_slider_range('hosttype_by_disc', publis_period),  radio_buttons=get_radio_buttons_chart_order('hosttype_by_disc'), comment = widgets_with_comment_dict["hosttype-by-disc"]), width=6),
                dbc.Col(widget_card_chart("hosttype_disc_scatter", "Positionnement des disciplines en fonction des voies privilégiées pour l'ouverture de leurs publications",
                        bsonat_iframe_src=widgets_with_iframe_dict['hosttype_disc_scatter'], slider_range=get_slider_range('hosttype_disc_scatter', publis_period), comment = widgets_with_comment_dict["hosttype-disc-scatter"]), width=6),
            ]
        ),
        html.Hr(),
    ]
)


layout = [row_widgets_header,
          html.Hr(className="my-2"),
          row_widgets]

######## UI CALLBACKS ##########
################################

for key in widgets_with_iframe_dict:
    @callback(
        Output(f"bsonat_modal_{key}", "is_open"),
        [Input(f"bsonat_open_{key}", "n_clicks"),
         Input(f"bsonat_close_{key}", "n_clicks")],
        [State(f"bsonat_modal_{key}", "is_open")],
        suppress_callback_exceptions=True
        # prevent_initial_call=True
    )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

########### CHARTS CALLBACKS ########################
#####################################################

# Callback set of publis data -> radar chart of disc
@callback(Output("fig_disc_repartition", "figure"),
          Input("disc_repartition-year-range", "value"))
def update_disc_radar(year_range):
    df = get_data()
    data = fn.get_filtered_data_by_year(df, "year", year_range)
    d = pd.DataFrame({'disc': data["bso_classification_fr"].value_counts(
    ).index, 'count': data["bso_classification_fr"].value_counts().values})
    fig = px.line_polar(d, r='count', theta='disc',
                        line_close=True, template=plotly_template)
    fig.update_traces(fill='toself')
    return fig

# Callback set of publis data -> stacked barchart of opened hostype percent by disc
@callback(
    Output('fig_hosttype_by_disc', 'figure'),
    [Input("hosttype_by_disc-year-range", "value"),
    Input("hosttype_by_disc-radio-chart-order", "value")]
)
def update_hosttype_rate_by_disc(year_range, chart_order):
    df = get_data()
    data = fn.get_filtered_data_by_year(df, "year", year_range)
    crosstab_df = fn.get_crosstab_percent(
        data, "bso_classification_fr", "oa_host_type_normalized")
    fig = px.bar(crosstab_df, y='bso_classification_fr', x=[
                 'Archive ouverte', 'Editeur', 'Editeur et archive ouverte'], orientation='h', color_discrete_map=colors, template=plotly_template)
    #fig.update_yaxes(categoryorder='total ascending')
    if chart_order == "oa":
        fig.update_yaxes(categoryorder='total ascending')
    else:
        fig.update_yaxes(categoryorder='array', categoryarray= top10_disc_list)
    fig.update_xaxes(title_text='Taux d\'accès ouvert')
    fig.update_yaxes(title_text='Disciplines')
    fig.update_traces(textposition='inside', texttemplate="%{value}"+"%")
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=-1.5
    ),
        margin=dict(l=10, r=10, t=10, b=10))
    return fig

# Callback set of publis data -> scatter plot of opened hostype percent by disc
@callback(
    Output('fig_hosttype_disc_scatter', 'figure'),
    Input("hosttype_disc_scatter-year-range", "value"),
)
def update_hosttype_disc_scatter(year_range):
    df = get_hosttype_exploded_data()
    data = fn.get_filtered_data_by_year(df,"year", year_range)
    d = pd.DataFrame({'disc': data["bso_classification_fr"].value_counts(
    ).index, 'count': data["bso_classification_fr"].value_counts().values})
    crosstab_df = (pd.crosstab(data["bso_classification_fr"],
                   data["oa_host_type_normalized_explode"], normalize='index')*100).round(1).reset_index()
    final_df = crosstab_df.merge(d, left_on='bso_classification_fr', right_on='disc').drop(
        columns='disc').reset_index()
    fig = px.scatter(
        final_df,
        x="Editeur",
        y="Archive ouverte",
        size="count",
        text="bso_classification_fr",
        color="bso_classification_fr",
        template=plotly_template
    )
    """fig.update_traces(marker=dict(
        line=dict(
            color='rgb(255, 111, 76)',
            width=2
        )
    ),
        selector=dict(mode='markers'))"""
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=10, r=10, t=10, b=10),
        transition={
            'duration': 800,
            'easing': 'cubic-in-out'
        },
    )
    fig.update_xaxes(
        title_text='Part des publications accessibles en OA depuis les sites éditeurs')
    fig.update_yaxes(
        title_text='Part des publications accessibles en OA sur une archive ouverte')
    return fig
