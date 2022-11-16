import pathlib
import pandas as pd
import dash
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
import dash_dvx as dvx
import sqlalchemy as sqla
import config

dash.register_page(__name__, path='/data-publications')

publis_last_obs_date = config.PUBLIS_LAST_OBS_DATE

# get relative data folder
PATH = pathlib.Path(__file__).parent
DB_PATH = PATH.joinpath("../db", "publications.db").resolve()

dbEngine=sqla.create_engine(f'sqlite:///{DB_PATH}')
df = pd.read_sql(f'select doi,year,genre,is_oa_normalized,oa_status_normalized from bso_publis_uniques_{publis_last_obs_date}',dbEngine)


layout = dbc.Row(dvx.Grid(
        id="grid",
        keyExpr="doi",
        selectionMode="none",
        columnChooserIsEnabled=True,
        pageSizeSelectorIsEnabled=True,
        allowedPageSizes=[5, 10, 20, 50],
        dataSource=df.to_dict(orient="records"),))