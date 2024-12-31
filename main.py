#!/bin/bash
import dash
import dash_bootstrap_components as dbc

external_stylesheets = [dbc.themes.BOOTSTRAP]


app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets,
                meta_tags=[{
                    "name": "viewport",
                    "content": "width=device-width"
                }])

server = app.server

app.config.suppress_callback_exceptions = True