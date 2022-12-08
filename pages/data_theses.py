import pathlib
import pandas as pd
import dash
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
import dash_dvx as dvx
import sqlalchemy as sqla
import config

dash.register_page(__name__, path='/data-theses')

theses_last_obs_date = config.THESES_LAST_OBS_DATE

# get relative data folder
PATH = pathlib.Path(__file__).parent
DB_PATH = PATH.joinpath("../db", "theses.db").resolve()

dbEngine=sqla.create_engine(f'sqlite:///{DB_PATH}')
query_cols = ["nnt",
             "titres_fr",
             "auteurs_0_nom",
             "directeurs_these_0_nom",
             "langue",
             "date_soutenance",
             "annee_civile_soutenance",
             "ecoles_doctorales_0_nom",
             "accessible_normalized",
             "embargo",
             "embargo_duree",
             "oai_set_specs_0_regroup_label"]
df = pd.read_sql(f"select {','.join(query_cols)} from bso_theses_uca_{theses_last_obs_date}",dbEngine)

row_title = html.H4(
                    "Baromètre des thèses : métadonnées source", className="p-3"
                )
row_grid = dbc.Row(dvx.Grid(
        id="grid",
        keyExpr="nnt",
        selectionMode="none",
        columnChooserIsEnabled=True,
        pageSizeSelectorIsEnabled=True,
        allowedPageSizes=[5, 10, 20, 50],
        defaultPageSize=5,
        dataSource=df.to_dict(orient="records"),
        columns = [{
                "dataField":"nnt",
                "caption":"NNT"
        },
                {
                "dataField":"titres_fr",
                "caption":"Titre"
        },
        {
                "dataField":"auteurs_0_nom",
                "caption":"Auteur"
        },
         {
                "dataField":"directeurs_these_0_nom",
                "caption":"Directeur"
        },
         {
                "dataField":"langue",
                "caption":"Langue"
        },
        {
                "dataField":"date_soutenance",
                "caption":"Date de soutenance"
        },
        {
                "dataField":"annee_civile_soutenance",
                "caption":"Année de soutenance"
        },
        {
                "dataField":"ecoles_doctorales_0_nom",
                "caption":"Ecole doctorale"
        },
        {
                "dataField":"accessible_normalized",
                "caption":"Accessible"
        },
        {
                "dataField":"embargo",
                "caption":"Date de fin d'embargo"
        },
        {
                "dataField":"embargo_duree",
                "caption":"Durée (en jours) de l'embargo"
        },
        {
                "dataField":"oai_set_specs_0_regroup_label",
                "caption":"Discipline"
        },]
        ))

layout = [
        row_title,
        row_grid
]