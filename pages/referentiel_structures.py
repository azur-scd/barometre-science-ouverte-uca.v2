import pathlib
import pandas as pd
import dash
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
import helpers.functions as fn
import plotly.express as px
import sqlalchemy as sqla
import dash_dvx as dvx
import json
import config

dash.register_page(__name__, path='/referentiel-structures')

#config params
publis_last_obs_date = config.PUBLIS_LAST_OBS_DATE

# get relative db folder
PATH = pathlib.Path(__file__).parent
DB_PATH = PATH.joinpath("../db", "publications.db").resolve()

dbEngine=sqla.create_engine(f'sqlite:///{DB_PATH}')

def get_referentiel(publis_obs_date):
        df = pd.read_sql(f'select * from referentiel_structures_{publis_obs_date}',dbEngine)
        return df
df_structures = get_referentiel(publis_last_obs_date)

row_title = html.H4(
                    "Référentiel des structures UCA", className="p-3"
                )

row_main = html.Div(
    dvx.List(
        id="list", 
        dataSource=json.loads(df_structures.to_json(orient="records")),
        keyExpr= "id",
        parentIdExpr= "parent_id",
        filterRowIsEnabled= False, #if you don't want the row filter undre the header
        columnChooserIsEnabled= True, #if you want to have the ability to show/hide columns in the UI
        defaultPageSize= 60,
        selectionMode="none", # if you want the parents and the childs nodes of the selected item, default config is "leavesOnly" wich returns only the sub-items of the selection
        columns= [
             {
             "dataField": 'id',
             "caption": 'id',
             "visible": False
           },
            {
             "dataField": 'parent_id',
             "caption": 'parent_id',
             "visible": False
           },
           {
             "dataField": 'affiliation_name',
             "caption": 'Structure'
           },
            {
             "dataField": 'RNSR',
             "caption": 'Identifiant RNSR'
           },
             {
             "dataField": 'HAL',
             "caption": 'Identifiant Aurehal'
           },
             {
             "dataField": 'ppn_valide',
             "caption": 'Identifiant Idref'
           },
             {
             "dataField": 'VIAF',
             "caption": 'Identifiant VIAF'
           },
             {
             "dataField": 'ISNI',
             "caption": 'Identifiant ISNI'
           },
             {
             "dataField": 'BNF',
             "caption": 'Identifiant BnF'
           },
             {
             "dataField": 'documents_count',
             "caption": 'Nombre de publications affiliées'
           },
        ]
    ),
)

layout = [row_title,
          #html.Hr(className="my-2"),
          row_main]