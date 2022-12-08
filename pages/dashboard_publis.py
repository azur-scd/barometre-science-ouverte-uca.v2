import pathlib
import pandas as pd
import dash
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from templates.ui_templates import get_slider_range, widget_card_chart, get_radio_buttons
from templates.header_templates import get_publis_row_widgets_header
import helpers.functions as fn
import plotly.express as px
import sqlalchemy as sqla
import dash_dvx as dvx
import json
import config

dash.register_page(__name__, path='/dashboard-publications')

#config params
publis_last_obs_date = config.PUBLIS_LAST_OBS_DATE
colors = config.COLORS
publis_obs_dates = config.PUBLIS_OBS_DATES
publis_period = config.PUBLIS_PERIOD
line_dash_map = config.LINE_DASH_MAP
plotly_template = config.PLOTLY_TEMPLATE


## For loop of callbacks on the bso modal url
widgets_with_iframe_dict = {"oa_rate_by_obs_date":"https://barometredelascienceouverte.esr.gouv.fr/integration/fr/publi.general.dynamique-ouverture.chart-taux-ouverture",
                            "oa_and_hosttype":"https://barometredelascienceouverte.esr.gouv.fr/integration/fr/publi.general.voies-ouverture.chart-repartition-publications",
                            "hosttype_rate_by_year":"https://barometredelascienceouverte.esr.gouv.fr/integration/fr/publi.general.voies-ouverture.chart-repartition-taux",
                            "oa_rate_compare":"https://barometredelascienceouverte.esr.gouv.fr/integration/fr/publi.general.dynamique-ouverture.chart-evolution-proportion",
                            "hosttype_by_genre": "https://barometredelascienceouverte.esr.gouv.fr/integration/fr/publi.general.genres-ouverture.chart-repartition-genres"}

widgets_with_comment_dict = {"oa-rate":"Ce graphique montre le taux d'ouverture global mesuré en 2022 pour les 14 607 publications UCA référencées dans Scopus de 2016 à 2021.",
                             "oa-rate-by-year": "Ce graphique détaille la proportion du taux d'accès ouvert mesuré en 2022 en fonction des dates de publication. Il permet de constater à la fois la croissance quantitative de la production scientifique issue de l'activité de recherche, ainsi que l'augmentation régulière (en valeur absolue et en pourcentage) du processus de mise à disposition en accès ouvert, révélant l'évolutions des pratiques de diffusion des chercheurs UCA.",
                             "oa-rate-by-obs-date": "Ce graphique montre plus précisément pour les 3 snapshots annuels successifs de données dont nous disposons le taux d'accès ouvert des publications parues l'année précédente. Entre 2020 et 2022 on observe donc une augmentation de presque 10 points du taux d'accès ouvert sur les publications les plus récentes qui traduit l'aspect évolutif des processus d'ouverture des publications. On note également que pour les publications parues en 2020 observées en 2021, le taux d'accès ouvert du périmètre UCA est supérieur de 6 points ua taux national.",
                             "oa-and-hosttype": "Ce graphique illustre les différents modèles économiques à l'oeuvre dans les dynamique d'ouverture des publications. On note ainsi que le double accès ouvert à la fois sur les plateformes éditeurs et via le dépôt en archive ouverte est au final la voie privilégiée pour l'accès libre aux publications UCA.",
                             "hosttype-rate-by-year": "Ce graphique montre la répartition par voie d'ouverture et par année de publication pour la denière observation en 2022, et donne à voir les mêmes tendances pour les publications UCA qu'au niveau naional, à savoir une proportion relativement stable et faible de l'ouverture en accès ouvert uniquement sur les plateformes éditeurs et un accroissement de la pratique de dépôt de preprints et postprints sur des archives ouvertes",
                             "oa-rate-compare": "Ce graphique présente, pour chaque date d'observation (chaque courbe), le taux d'accès ouvert des publications UCA par date de publication. On constate ainsi, pour chaque année de publication observée à une date différente, que le taux d'ouverture correspondant augmente au fur et à mesure du temps, témoignant de la dynamique à l'oeuvre dans les dispositifs de libération des publications (barrières mobiles, levées d'embargo, dépôts en achive ouverte...) ainsi que de la réduction progressive du délai de mise à disposition en opan access des publications."
                             }

# get relative db folder
PATH = pathlib.Path(__file__).parent
DB_PATH = PATH.joinpath("../db", "publications.db").resolve()

dbEngine=sqla.create_engine(f'sqlite:///{DB_PATH}')

def get_publis_dataset(publis_obs_date,selected_structure):
    if selected_structure == "0":
        df = pd.read_sql(f'select doi, year, genre, is_oa_normalized, oa_status_normalized, oa_host_type_normalized from bso_publis_uniques_{publis_obs_date} where year < {int(publis_obs_date[:4])}',dbEngine)
    else:
        df = pd.read_sql(f'SELECT bso_publis_uniques_{publis_obs_date}.doi,bso_publis_uniques_{publis_obs_date}.year,bso_publis_uniques_{publis_obs_date}.genre,bso_publis_uniques_{publis_obs_date}.is_oa_normalized,bso_publis_uniques_{publis_obs_date}.oa_status_normalized, bso_publis_uniques_{publis_obs_date}.oa_host_type_normalized FROM bso_publis_uniques_{publis_obs_date} JOIN bso_publis_all_by_affiliation_{publis_obs_date} ON bso_publis_uniques_{publis_obs_date}.doi = bso_publis_all_by_affiliation_{publis_obs_date}.doi WHERE bso_publis_all_by_affiliation_{publis_obs_date}.aff_internal_id = {selected_structure} and bso_publis_uniques_{publis_obs_date}.year < {int(publis_obs_date[:4])}',dbEngine)
    return df

def get_crosstab_by_date_obs(selected_structure):
    publis_crosstab_dataframes_dict = dict()
    appended_data = []
    # dict of dataframes
    for date in publis_obs_dates:
        publis_crosstab_dataframes_dict[f'publis_crosstab_{date}'] = fn.get_crosstab_percent(get_publis_dataset(date,selected_structure), "year", "is_oa_normalized")
        publis_crosstab_dataframes_dict[f'publis_crosstab_{date}']["year_obs"] = str(date[:4])
        appended_data.append(publis_crosstab_dataframes_dict[f'publis_crosstab_{date}'])
    appended_data = pd.concat(appended_data)
    #appended_data['year'] = appended_data['year'].astype('category')
    for column_name in ['year', 'year_obs']:
        appended_data[column_name] = appended_data[column_name].astype('string')
    #appended_data = appended_data.drop(columns=['index'])
    return appended_data

def create_json_structures():
    df_structures = pd.read_sql(f'select id,affiliation_name,documents_count from referentiel_structures_{publis_last_obs_date} where parent_id != 0 ORDER BY documents_count DESC',dbEngine)
    df_structures["label"] = df_structures["affiliation_name"].map(str) + " (" + df_structures["documents_count"].map(str) + " publications)"
    df_structures = df_structures.rename(columns={'id': 'value'})
    dict_structures = df_structures.to_dict('records')
    dict_structures.insert(0, {'value': 0, 'label': 'UCA toutes structures'})
    return dict_structures
dict_structures = create_json_structures()

row_widgets_header = html.Div(
    [
        dbc.Row(
            [  # stores of data
                html.Div(dcc.Store(id="publis_dataset")),
                # widgets
                html.Div(id="widgets-header"),
                #dbc.Col(widget_card_header("nb publis", "14 500"),width=2),
            ],
            align="center"
        ),
    ]
)
select_structure_section = dbc.Row([
    dbc.Col(html.H5("Sélectionner une structure de recherche"),width=4),
    dbc.Col( dbc.Select(
    id="selected_structure",
    options=dict_structures,
    value="0"
),
width=4)
],
className="fst-italic fw-bold bg-opacity-25 p-2 m-1 bg-primary text-light border rounded-pill")

compare_oa_form = dbc.Form(
    [dbc.Row(
        [
            dbc.Label("Publications observées en :", width="auto"),
            dbc.Col(
                dcc.Dropdown(
                 id="comp_last_date",
                 options=[{'label': str(date[:4]), 'value': str(date)} for date in publis_obs_dates],
                 value=publis_last_obs_date
              ),
                className="me-3",
                width=3
            ),
            dbc.Label("et en :", width="auto"),
            dbc.Col(
                dcc.Dropdown(
                  id="comp_first_date",
                  options=[{'label': str(date[:4]), 'value': str(date)} for date in publis_obs_dates],
                  value="20201130"
                ),
                className="me-3",
                width=3
            ),
        ],
        className="g-2",
    ),
    dbc.Row(
         [dbc.Label("étant passées de : ", width="auto"),
            dbc.Col(dcc.Dropdown(
            id="comp_first_oa_state",
            options=[
                {"label": "Accès fermé -> Accès ouvert", "value": "Accès fermé"},
                {"label": "Accès ouvert -> Accès fermé", "value": "Accès ouvert"},
            ],
            value="Accès fermé"
        ), width=8)
    ],className="g-2")
])

datatype_options = [
                    {"label": "Valeur absolue", "value": "qte"},
                    {"label": "Pourcentage", "value": "percent"},
                ] 

row_charts = html.Div(
    [   dbc.Row(
            [
                dbc.Col([widget_card_chart("oa_rate","Taux d'accès ouvert global",slider_range=get_slider_range("oa-rate", publis_period), comment = widgets_with_comment_dict["oa-rate"])], width=4),
                dbc.Col(widget_card_chart("oa_rate_by_year","Accès ouvert par année de publication",radio_buttons=get_radio_buttons("oa-rate", "Type de données :", datatype_options), comment = widgets_with_comment_dict["oa-rate-by-year"]), width=4),
                dbc.Col(widget_card_chart("oa_rate_by_obs_date","Taux d'accès ouvert des publications parues durant l'année précédente par année d'observation", bsonat_iframe_src=widgets_with_iframe_dict['oa_rate_by_obs_date'], comment = widgets_with_comment_dict["oa-rate-by-obs-date"]), width=4),
            ]
        ),
        html.Hr(),
         dbc.Row(
            [
                dbc.Col(widget_card_chart("oa_and_hosttype","Répartition des publications par voie d'ouverture",bsonat_iframe_src=widgets_with_iframe_dict['oa_and_hosttype'], slider_range=get_slider_range("oa-and-hosttype", publis_period), comment = widgets_with_comment_dict["oa-and-hosttype"]), width=6),
                dbc.Col(widget_card_chart("hosttype_rate_by_year","Répartition des publications en accès ouvert par voie d\'ouverture et par année de publication",bsonat_iframe_src=widgets_with_iframe_dict['hosttype_rate_by_year'], comment = widgets_with_comment_dict["hosttype-rate-by-year"]), width=6),
            ]
        ),
        html.Hr(),
         dbc.Row(
            [
                dbc.Col(widget_card_chart("oa_rate_compare","Évolution du taux d'accès ouvert des publications par année d'observation et date de publication",bsonat_iframe_src=widgets_with_iframe_dict['oa_rate_compare'], comment = widgets_with_comment_dict["oa-rate-compare"]), width=6),
                dbc.Col([
            dbc.Card([
            dbc.CardHeader(
                 dbc.Row(
                    [
                        dbc.Col(html.H2("Focus sur les publications ayant changé de type d'accès entre deux dates d'observation",
                                        className="fs-5 fw-bold mb-0"), width=12),
                    ]
                )
            ),
            dbc.CardBody([
                compare_oa_form,
                html.Div(id="oa_compare_datagrid")])
           ])], width=6),
            ]
        ),
        html.Hr(),
         dbc.Row(
            [
                dbc.Col(widget_card_chart("hosttype_by_genre","Taux d'accès ouvert et voies d'ouverture par type de publications",bsonat_iframe_src=widgets_with_iframe_dict['hosttype_by_genre'],  slider_range=get_slider_range("hosttype-by-genre", publis_period)), width=6),
                #dbc.Col(widget_card_chart("hosttype_rate_by_year","Répartition des publications en accès ouvert par voie d\'ouverture et par année de publication",bsonat_iframe_src=widgets_with_iframe_dict['hosttype_rate_by_year']), width=6),
            ]
        ),
    ]
)


layout = [row_widgets_header,
          html.Hr(className="my-2"),
          select_structure_section,
          html.Hr(className="my-2"),
          row_charts]

######## UI CALLBACKS ##########
################################

for key in widgets_with_iframe_dict:
    @callback(
          Output(f"bsonat_modal_{key}", "is_open"),
          [Input(f"bsonat_open_{key}", "n_clicks"), Input(f"bsonat_close_{key}", "n_clicks")],
          [State(f"bsonat_modal_{key}", "is_open")],
          suppress_callback_exceptions=True
          #prevent_initial_call=True
    )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

########## STORE DATA CALLBACKS #####################
#####################################################

@callback(
    Output('publis_dataset', 'data'),
    Input("selected_structure", "value")
)
def update_publis_dataset(selected_structure):
    json_publis_dataset = get_publis_dataset(publis_last_obs_date,selected_structure).to_dict(orient="records")
    return json.dumps(json_publis_dataset)

########### WIDGETS HEADER CALLBACKS ################
#####################################################

"""@callback(
    Output("nb_publis_total", "children"),
    Output("oa_rate_total", "children"),
    Input("publis_dataset", "data")
)
def widgets_header(publis_dataset):
    df = pd.read_json(publis_dataset)
    nb_publis_total = df.shape[0]
    oa_rate_total = round(int(df[df["is_oa_normalized"] == "Accès ouvert"].shape[0]) * 100 / int(nb_publis_total),1)
    return nb_publis_total,f"{oa_rate_total} %"
    """

@callback(
    Output("widgets-header", "children"),
    Input("publis_dataset", "data")
)
def widgets_header(publis_dataset):
    df = pd.read_json(publis_dataset)
    return get_publis_row_widgets_header(df)


########### CHARTS CALLBACKS ########################
#####################################################

## Callback set of publis data -> pie chart
@callback(
    Output('fig_oa_rate', 'figure'),
    [Input("publis_dataset", "data"),
    Input("oa-rate-year-range","value")],
)
def update_oa_rate(publis_dataset, year_range):
    df = pd.read_json(publis_dataset)
    data = fn.get_filtered_data_by_year(df,"year",year_range)
    fig = px.pie(data, names='is_oa_normalized', hole=0.7, color="is_oa_normalized", color_discrete_map= colors)
    return fig

## Callback set of publis data -> vertical barchart oa rate by year
@callback(
    Output('fig_oa_rate_by_year', 'figure'),
    [Input("publis_dataset", "data"),
    Input("oa-rate-radio-buttons","value")],
)
def update_oa_rate_by_year(publis_dataset, radio_buttons):
    df = pd.read_json(publis_dataset)
    crosstab_df = fn.get_crosstab_simple(df, "year", "is_oa_normalized")
    crosstab_percent_df = fn.get_crosstab_percent(df, "year", "is_oa_normalized")
    if radio_buttons == "qte":
        fig = px.bar(crosstab_df, x='year',
                     y=["Accès ouvert", "Accès fermé"], color_discrete_map=colors, template=plotly_template)
        fig.update_yaxes(title_text='Nombre de publications')
        fig.update_traces(textposition='inside',texttemplate = "%{value}")
    if radio_buttons == "percent":
        fig = px.bar(crosstab_percent_df, x='year',
                     y=["Accès ouvert", "Accès fermé"], color_discrete_map=colors, template=plotly_template)
        fig.update_yaxes(title_text='Taux d\'ouverture')
        fig.update_traces(textposition='inside',texttemplate = "%{value}"+"%")
    fig.update_xaxes(title_text='Année de publication')
    fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
    ),
    margin=dict(l=10, r=10, t=10, b=10))
    return fig

## Callback set of publis data -> horizontal barchart oa rate by observation date
@callback(
    Output('fig_oa_rate_by_obs_date', 'figure'),
    Input('selected_structure', 'value'),
)
def update_oa_rate_by_obs_date(selected_structure):
    df = get_crosstab_by_date_obs(selected_structure)
    list_date_obs = [d[:4] for d in publis_obs_dates]
    list_preceding_year = [str(int(d) - 1) for d in list_date_obs]
    data = df[df.set_index(['year','year_obs']).index.isin(zip(list_preceding_year,list_date_obs))]
    print(data)
    fig = px.bar(data, y='year_obs', x='Accès ouvert', orientation='h',color_discrete_sequence=[colors['Accès ouvert']], template=plotly_template)
    fig.update_xaxes(title_text='Taux d\'ouverture')
    fig.update_yaxes(title_text='Année d\'observation', categoryorder='category ascending')
    fig.update_traces(textposition='inside',texttemplate = "%{value}"+"%")
    return fig

## Callback set of publis data -> treemap oa and host type
@callback(
    Output('fig_oa_and_hosttype', 'figure'),
    [Input('publis_dataset', 'data'),
    Input("oa-and-hosttype-year-range","value")]
)
def update_oa_and_hosttype(publis_dataset, year_range):
    df = pd.read_json(publis_dataset)
    data = fn.get_filtered_data_by_year(df,"year",year_range)
    fig = px.treemap(data, path=['is_oa_normalized', 'oa_host_type_normalized'], maxdepth=2,color='oa_host_type_normalized',color_discrete_map= colors)
    fig.update_traces(textinfo = "label+value+percent parent+percent entry")
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
    return fig

## Callback set of publis data -> stacked barchart of opened hostype percent by year
@callback(
    Output('fig_hosttype_rate_by_year', 'figure'),
    Input('publis_dataset', 'data'),
)
def update_hosttype_rate_by_year(publis_dataset):
    df = pd.read_json(publis_dataset)
    crosstab_df = fn.get_crosstab_percent(df, "year", "oa_host_type_normalized")
    fig = px.bar(crosstab_df, x='year', y=['Archive ouverte', 'Editeur', 'Editeur et archive ouverte'], color_discrete_map=colors, template=plotly_template)
    fig.update_xaxes(title_text='Année de publication')
    fig.update_yaxes(title_text='Taux d\'accès ouvert')
    fig.update_traces(textposition='inside',texttemplate = "%{value}"+"%")
    fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
    ),
    margin=dict(l=10, r=10, t=10, b=10))
    return fig

## Callback selected structure -> dict of crosstab dataset dict -> lines chart of oa rate by year and observation date
@callback(
    Output('fig_oa_rate_compare', 'figure'),
    Input("selected_structure", "value"),
)
def update_fig_oa_rate_compare(selected_structure):
    df = get_crosstab_by_date_obs(selected_structure)
    fig = px.line(df.sort_values(by=['year'], ascending=[True]), x='year', y='Accès ouvert', line_group='year_obs', text="Accès ouvert",color_discrete_sequence=[colors["Accès ouvert"]], line_dash='year_obs', line_dash_map=line_dash_map, template=plotly_template)
    fig.update_traces(connectgaps=False,mode="lines+markers+text",textposition='top center')
    fig.update_xaxes(title_text='Année de publication')
    fig.update_layout(legend_title_text='Année d\'observation')
    return fig

@callback(
    Output("oa_compare_datagrid", "children"),
    Input('comp_last_date','value'),
    Input('comp_first_date', 'value'),
    Input('comp_first_oa_state', 'value'),
    Input("selected_structure", "value"),
)
def update_grid_oa_rate_compare(comp_last_date,comp_first_date,comp_first_oa_state,selected_structure):
    if selected_structure == "0":
        df = pd.read_sql(f'select distinct(bso_publis_uniques_{comp_last_date}.doi) as doi, bso_publis_uniques_{comp_last_date}.year, bso_publis_uniques_{comp_last_date}.title, '
                       f'bso_publis_uniques_{comp_last_date}.publisher_by_doiprefix, bso_publis_uniques_{comp_last_date}.is_oa_normalized, bso_publis_uniques_{comp_last_date}.oa_status_normalized '
                       f'FROM bso_publis_uniques_{comp_last_date} JOIN bso_publis_uniques_{comp_first_date} ON bso_publis_uniques_{comp_last_date}.doi = bso_publis_uniques_{comp_first_date}.doi '
                       f'WHERE bso_publis_uniques_{comp_first_date}.is_oa_normalized = "{comp_first_oa_state}" '
                       f'AND bso_publis_uniques_{comp_last_date}.is_oa_normalized <> bso_publis_uniques_{comp_first_date}.is_oa_normalized' ,dbEngine)
    else :
        df = pd.read_sql(f'select distinct(bso_publis_uniques_{comp_last_date}.doi) as doi, bso_publis_uniques_{comp_last_date}.year, bso_publis_uniques_{comp_last_date}.title, '
                       f'bso_publis_uniques_{comp_last_date}.publisher_by_doiprefix, bso_publis_uniques_{comp_last_date}.is_oa_normalized, bso_publis_uniques_{comp_last_date}.oa_status_normalized '
                       f'FROM bso_publis_uniques_{comp_last_date} JOIN bso_publis_uniques_{comp_first_date} ON bso_publis_uniques_{comp_last_date}.doi = bso_publis_uniques_{comp_first_date}.doi '
                       f'JOIN bso_publis_all_by_affiliation_{comp_last_date} ON bso_publis_uniques_{comp_last_date}.doi = bso_publis_all_by_affiliation_{comp_last_date}.doi '
                       f'WHERE bso_publis_all_by_affiliation_{comp_last_date}.aff_internal_id = {selected_structure} AND bso_publis_uniques_{comp_first_date}.is_oa_normalized = "{comp_first_oa_state}" '
                       f'AND bso_publis_uniques_{comp_last_date}.is_oa_normalized <> bso_publis_uniques_{comp_first_date}.is_oa_normalized' ,dbEngine)
    div_datagrid = dvx.Grid(
        id="grid", 
        dataSource=json.loads(df.to_json(orient="records")),
        keyExpr= "doi",
        searchPanelIsEnabled= True, #if you don't want the search bar
        pageSizeSelectorIsEnabled= True, #if you want to have the ability to change in the UI the defalt number of itmes by page
        allowedPageSizes= [5, 10, 20, 50, 100],
        defaultPageSize=5,
        columnChooserIsEnabled = True
    )
    return div_datagrid

## Callback set of publis data -> stacked barchart of opened hostype percent by genre
@callback(
    Output('fig_hosttype_by_genre', 'figure'),
    [Input('publis_dataset', 'data'),
    Input("hosttype-by-genre-year-range","value")]
)
def update_hosttype_by_genre(publis_dataset, year_range):
    df = pd.read_json(publis_dataset)
    data = fn.get_filtered_data_by_year(df,"year",year_range)
    crosstab_df = fn.get_crosstab_percent(data, "genre", "oa_host_type_normalized")
    fig = px.bar(crosstab_df, x='genre', y=['Archive ouverte', 'Editeur', 'Editeur et archive ouverte'], color_discrete_map=colors, template=plotly_template)
    fig.update_xaxes(title_text='Type de publication')
    fig.update_yaxes(title_text='Taux d\'accès ouvert')
    fig.update_traces(textposition='inside',texttemplate = "%{value}"+"%")
    fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
    ),
    margin=dict(l=10, r=10, t=10, b=10))
    return fig