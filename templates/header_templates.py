import pathlib
import pandas as pd
import dash
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from templates.ui_templates import widget_card_header
import config

publis_period = config.PUBLIS_PERIOD
theses_period = config.THESES_PERIOD
publis_last_obs_date_text = config.PUBLIS_LAST_OBS_DATE_TEXT
theses_last_obs_date_text = config.THESES_LAST_OBS_DATE_TEXT

def get_publis_row_widgets_header(df):
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(widget_card_header("nb_publis_total", "Nombre de publications",
                                               text=df.shape[0]), width={"offset": 1, "size": 2}),
                    dbc.Col(widget_card_header("oa_rate_total", "Taux d'accès ouvert",
                                               text=f'{round(int(df[df["is_oa_normalized"] == "Accès ouvert"].shape[0]) * 100 / int(df.shape[0]),1)} %'), width=2),
                    dbc.Col(widget_card_header(
                        "period", "Période observée", text=f"{publis_period[0]} - {str(int(publis_period[1]) - 1)}"), width=2),
                    dbc.Col(widget_card_header(
                        "last_obs", "Date de dernière mise à jour", text=f"{publis_last_obs_date_text}"), width=2),
                    dbc.Col(widget_card_header(
                        "source", "Source des données", text="Scopus"), width=2),
                ],
                align="center"
            ),
        ]
    )

def get_theses_row_widgets_header(df):
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(widget_card_header("nb_theses_total", "Nombre de thèses soutenues",
                                               text=df.shape[0]), width={"offset": 1, "size": 2}),
                    dbc.Col(widget_card_header("oa_rate_total", "Taux d'accès libre",
                                               text=f'{round(int(df[df["accessible_normalized"] == "Accès libre"].shape[0]) * 100 / int(df.shape[0]),1)} %'), width=2),
                    dbc.Col(widget_card_header(
                        "period", "Période observée", text=f"{theses_period[0]} - {str(int(theses_period[1]) - 1)}"), width=2),
                    dbc.Col(widget_card_header(
                        "last_obs", "Date de dernière mise à jour", text=f"{theses_last_obs_date_text}"), width=2),
                    dbc.Col(widget_card_header(
                        "source", "Source des données", text="theses.fr / data.gouv.fr"), width=2),
                ],
                align="center"
            ),
        ]
    )
