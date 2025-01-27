#!/bin/bash
from dash import Dash, _dash_renderer
import dash_mantine_components as dmc


_dash_renderer._set_react_version("18.2.0")
app = Dash(__name__,
           suppress_callback_exceptions=True,
           use_pages=True,
           pages_folder='apps',
           external_stylesheets=dmc.styles.ALL
        )

server = app.server

app.config.suppress_callback_exceptions = True
