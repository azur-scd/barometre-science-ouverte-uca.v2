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
query_cols = ["source_id",
              "doi",
              "title",
              "all_authors",
              "year",
              "genre",
              "publisher_by_doiprefix",
              "is_oa_normalized",
              "oa_status_normalized",
              "oa_host_type_normalized",
              "bso_classification_fr"]
df = pd.read_sql(f"select {','.join(query_cols)} from bso_publis_uniques_{publis_last_obs_date}",dbEngine)

row_title = html.H4(
                    "Baromètre des publications : métadonnées source", className="p-3"
                )

row_grid = dbc.Row(dvx.Grid(
        id="grid",
        keyExpr="doi",
        selectionMode="none",
        columnChooserIsEnabled=True,
        pageSizeSelectorIsEnabled=True,
        allowedPageSizes=[5, 10, 20, 50],
        defaultPageSize=5,
        dataSource=df.to_dict(orient="records"),
        columns = [{
                "dataField":"source_id",
                "caption":"Scopus ID"
        },
                {
                "dataField":"doi",
                "caption":"DOI"
        },
        {
                "dataField":"title",
                "caption":"Titre"
        },
        {
                "dataField":"all_authors",
                "caption":"Auteurs"
        },
        {
                "dataField":"year",
                "caption":"Année de publication"
        },
        {
                "dataField":"genre",
                "caption":"Type de publication"
        },
        {
                "dataField":"publisher_by_doiprefix",
                "caption":"Editeur"
        },
        {
                "dataField":"is_oa_normalized",
                "caption":"Open Access"
        },
        {
                "dataField":"oa_status_normalized",
                "caption":"Voie OA"
        },
        {
                "dataField":"oa_host_type_normalized",
                "caption":"Hébergement OA"
        },
        {
                "dataField":"bso_classification_fr",
                "caption":"Discipline"
        }]
        ))

layout = [
        row_title,
        row_grid
]