import pathlib
import pandas as pd
import dash
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from templates.ui_templates import get_slider_range, widget_card_header, widget_card_chart, get_select_publisher, get_radio_buttons_chart_order
from templates.header_templates import get_row_widgets_header
import helpers.functions as fn
import plotly.express as px
import sqlalchemy as sqla
import json
import config

dash.register_page(__name__, path='/dashboard-publications-editeurs')

# config params
publis_last_obs_date = config.PUBLIS_LAST_OBS_DATE
publis_obs_dates = config.PUBLIS_OBS_DATES
colors = config.COLORS
plotly_template = config.PLOTLY_TEMPLATE

# For loop of callbacks on the bso modal url
widgets_with_iframe_dict = {"pub_oa_rate_by_obs_date": "https://barometredelascienceouverte.esr.gouv.fr/integration/fr/publi.publishers.dynamique-ouverture.chart-taux-ouverture",
                            "hosttype_by_pub": "https://barometredelascienceouverte.esr.gouv.fr/integration/fr/publi.publishers.politiques-ouverture.chart-classement",
                            "pub_oa_status": "https://barometredelascienceouverte.esr.gouv.fr/integration/fr/publi.publishers.type-ouverture.chart-repartition-modeles",
                            "hosttype_pub_scatter": "https://barometredelascienceouverte.esr.gouv.fr/integration/fr/publi.publishers.politiques-ouverture.chart-comparaison"
                            }

# get relative db folder
PATH = pathlib.Path(__file__).parent
DB_PATH = PATH.joinpath("../db", "publications.db").resolve()

dbEngine = sqla.create_engine(f'sqlite:///{DB_PATH}')

def get_publis_dataset(publis_obs_date,selected_publisher):
    if selected_publisher == "Tous les éditeurs":
        df = pd.read_sql(f'select doi, year, is_oa_normalized, oa_host_type_normalized, oa_status_normalized, publisher_by_doiprefix from bso_publis_uniques_{publis_obs_date}  where publisher_by_doiprefix is not NULL',dbEngine)
    else:
        df = pd.read_sql(f'select doi, year, is_oa_normalized, oa_host_type_normalized, oa_status_normalized, publisher_by_doiprefix from bso_publis_uniques_{publis_last_obs_date} where publisher_by_doiprefix = "{selected_publisher}"',dbEngine)
    return df

def get_crosstab_by_date_obs(selected_publisher):
    publis_crosstab_dataframes_dict = dict()
    appended_data = []
    # dict of dataframes
    for date in publis_obs_dates:
        publis_crosstab_dataframes_dict[f'publis_crosstab_{date}'] = fn.get_crosstab_percent(get_publis_dataset(date,selected_publisher), "year", "is_oa_normalized")
        publis_crosstab_dataframes_dict[f'publis_crosstab_{date}']["year_obs"] = str(date[:4])
        appended_data.append(publis_crosstab_dataframes_dict[f'publis_crosstab_{date}'])
    appended_data = pd.concat(appended_data)
    for column_name in ['year', 'year_obs']:
        appended_data[column_name] = appended_data[column_name].astype('string')
    return appended_data

def get_publishers_count_data(limit=None):
    if limit is not None:
        df = pd.read_sql(
        f'SELECT publisher_by_doiprefix, count(*) as count FROM bso_publis_uniques_{publis_last_obs_date}  where publisher_by_doiprefix is not NULL GROUP BY publisher_by_doiprefix ORDER BY count DESC LIMIT {limit}', dbEngine)
    else:
        df = pd.read_sql(
        f'SELECT publisher_by_doiprefix, count(*) as count FROM bso_publis_uniques_{publis_last_obs_date}  where publisher_by_doiprefix is not NULL GROUP BY publisher_by_doiprefix ORDER BY count DESC', dbEngine)
    return df

def get_hosttype_exploded_data():
    df = get_publis_dataset(publis_last_obs_date,"Tous les éditeurs")
    df['oa_host_type_normalized_tmp'] = df['oa_host_type_normalized'].apply(
        lambda x: ["Editeur", "Archive ouverte"] if (x == "Editeur et archive ouverte") else list(x.split(",")))
    data = df.assign(oa_host_type_normalized_explode=df['oa_host_type_normalized_tmp']).explode(
        'oa_host_type_normalized_explode').drop(columns=['oa_host_type_normalized_tmp', 'oa_host_type_normalized'])
    return data

def create_json_publishers():
    df = get_publishers_count_data()
    df["value"] = df["publisher_by_doiprefix"]
    data_dict = df.rename(columns={"publisher_by_doiprefix":"label"}).drop(columns="count").to_dict(orient="records")
    data_dict.insert(0, {'value': 'Tous les éditeurs', 'label': 'Tous les éditeurs'})
    return data_dict

dict_publishers = create_json_publishers()
top25_pub_list = [s["publisher_by_doiprefix"] for s in get_publishers_count_data(limit=25).to_dict("records")]
top10_pub_list = [s["publisher_by_doiprefix"] for s in get_publishers_count_data(limit=10).to_dict("records")]
#top25_pub_list = [s["label"] for s in dict_publishers[1:26]]
df = get_publis_dataset(publis_last_obs_date,"Tous les éditeurs")

row_widgets_header = get_row_widgets_header(df)

row_widgets = html.Div([

     dbc.Row(
            [
                dbc.Col(widget_card_chart("pub_oa_rate_by_obs_date", "Part des publications mises à disposition en accès ouvert par leur éditeur, par année d’observation, pour les publications parues durant l’année précédente",
                        bsonat_iframe_src=widgets_with_iframe_dict['pub_oa_rate_by_obs_date'], select_publisher=get_select_publisher('pub_oa_rate_by_obs_date', dict_publishers)), width=6),
                dbc.Col(widget_card_chart("hosttype_by_pub", "Modalités d'ouverture des publications chez les éditeurs ou plateformes de publication les plus importants en volume (top 25)",
                        bsonat_iframe_src=widgets_with_iframe_dict['hosttype_by_pub'], slider_range=get_slider_range('hosttype_by_pub'), radio_buttons=get_radio_buttons_chart_order('hosttype_by_pub')), width=6),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(widget_card_chart("pub_oa_status", "Répartition des modèles économiques pour les articles diffusés en accès ouvert par leur éditeur",
                        bsonat_iframe_src=widgets_with_iframe_dict['pub_oa_status'], slider_range=get_slider_range('pub_oa_status'), select_publisher=get_select_publisher('pub_oa_status', dict_publishers)), width=6),
                dbc.Col(widget_card_chart("hosttype_pub_scatter", "Positionnement des éditeurs et plateformes de publication (top 10) en fonction des voies privilégiées pour l'ouverture des publications",
                        bsonat_iframe_src=widgets_with_iframe_dict['hosttype_pub_scatter'], slider_range=get_slider_range('hosttype_pub_scatter')), width=6),
                
            ]
        ),
])

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

## Callback set of publis data -> horizontal barchart oa rate by observation date
@callback(
    Output('fig_pub_oa_rate_by_obs_date', 'figure'),
    Input('pub_oa_rate_by_obs_date-selected_publisher', 'value'),
)
def update_oa_rate_by_obs_date(selected_publisher):
    df = get_crosstab_by_date_obs(selected_publisher)
    list_date_obs = [d[:4] for d in publis_obs_dates]
    list_preceding_year = [str(int(d) - 1) for d in list_date_obs]
    data = df[df.set_index(['year','year_obs']).index.isin(zip(list_preceding_year,list_date_obs))]
    fig = px.bar(data, y='year_obs', x='Accès ouvert', orientation='h',color_discrete_sequence=[colors['Accès ouvert']], template=plotly_template)
    fig.update_xaxes(title_text='Taux d\'ouverture')
    fig.update_yaxes(title_text='Année d\'observation', categoryorder='category ascending')
    fig.update_traces(textposition='inside',texttemplate = "%{value}"+"%")
    return fig

# Callback set of publis data -> stacked barchart of opened hostype percent by pub
@callback(
    Output('fig_hosttype_by_pub', 'figure'),
    [Input("hosttype_by_pub-year-range", "value"),
    Input("hosttype_by_pub-radio-chart-order", "value")]
)
def update_hosttype_rate_by_pub(year_range, chart_order):
    data = fn.get_filtered_data_by_year(df, year_range)
    top25_data = data[data["publisher_by_doiprefix"].isin(top25_pub_list)]
    crosstab_df = fn.get_crosstab_percent(
        top25_data, "publisher_by_doiprefix", "oa_host_type_normalized")
    fig = px.bar(crosstab_df, y='publisher_by_doiprefix', x=[
                 'Archive ouverte', 'Editeur', 'Editeur et archive ouverte','Accès fermé'], orientation='h', height=800, color_discrete_map=colors, template=plotly_template)
    if chart_order == "oa":
        fig.update_yaxes(categoryorder='total ascending')
    else:
        top25_pub_list.reverse()
        fig.update_yaxes(categoryorder='array', categoryarray= top25_pub_list)
    fig.update_xaxes(title_text='Taux d\'accès ouvert')
    fig.update_yaxes(title_text='Editeurs')
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

# Callback set of publis data -> treemap oa_status
@callback(
    Output('fig_pub_oa_status', 'figure'),
    [Input("pub_oa_status-year-range","value"),
    Input('pub_oa_status-selected_publisher', 'value')]
)
def update_pub_oa_status(year_range, selected_publisher):
    df = get_publis_dataset(publis_last_obs_date,selected_publisher)
    data = fn.get_filtered_data_by_year(df[df["is_oa_normalized"] != "Accès fermé"], year_range)    
    fig = px.treemap(data, path=['oa_status_normalized'], maxdepth=2,color='oa_status_normalized',color_discrete_map= colors)
    fig.update_traces(textinfo = "label+value+percent entry")
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
    return fig

# Callback set of publis data -> scatter plot of opened hostype percent by publisher
@callback(
    Output('fig_hosttype_pub_scatter', 'figure'),
    Input("hosttype_pub_scatter-year-range", "value"),
)
def update_hosttype_pub_scatter(year_range):
    df = get_hosttype_exploded_data()
    data = fn.get_filtered_data_by_year(df, year_range)
    data = data[data["publisher_by_doiprefix"].isin(top10_pub_list)]
    d = pd.DataFrame({'pub': data["publisher_by_doiprefix"].value_counts(
    ).index, 'count': data["publisher_by_doiprefix"].value_counts().values})
    crosstab_df = (pd.crosstab(data["publisher_by_doiprefix"],
                   data["oa_host_type_normalized_explode"], normalize='index')*100).round(1).reset_index()
    final_df = crosstab_df.merge(d, left_on='publisher_by_doiprefix', right_on='pub').drop(
        columns='pub').reset_index()
    fig = px.scatter(
        final_df,
        x="Editeur",
        y="Archive ouverte",
        size="count",
        text="publisher_by_doiprefix",
        color="publisher_by_doiprefix",
        template=plotly_template,
        height= 800
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
