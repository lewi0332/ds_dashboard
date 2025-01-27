#!/usr/bin/env python3
"""
Main file to run the app. 

'python index.py' will run the app on your local machine.

Auther: Derrick Lewis
"""
import os
from dash import  dcc, html, callback, page_registry, page_container
from dash.dependencies import Input, Output, State
import plotly.io as pio
import dash_mantine_components as dmc
from plotly_theme_light import plotly_light
from main import app
from dash_iconify import DashIconify
from apps.form import form_layout

pio.templates["plotly_light"] = plotly_light
pio.templates.default = "plotly_light"

COMPANY_LOGO = "DATALOGO.jpg"

dropdown_disc = dmc.Stack(mt="md",
                          gap=0,
                          children=[
                          dmc.NavLink(
                              label=page['name'],
                              href=page["path"],
                              id={"type": 'navlink_navbar', "index": page["path"]}
                              )
                           for page in page_registry.values()
                           ]
                        )

layout = [
    dcc.Location(id="url", refresh="callback-nav"),
    dmc.Drawer(
        id="form_drawer",
        padding="md",
        position="right",
        size="50%",
    ),
    dmc.AppShell(
    [
        dmc.AppShellHeader(
            dmc.Group(
                style={"display": "flex", "justifyContent": "space-between"},
                children=[
                    dmc.Group(
                        children=[
                            dmc.Burger(
                                id="mobile-burger",
                                size="sm",
                                hiddenFrom="sm",
                                opened=False,
                            ),
                            dmc.Burger(
                                id="desktop-burger",
                                size="sm",
                                visibleFrom="sm",
                                opened=False,
                            ),
                            dmc.Image(src=app.get_asset_url(COMPANY_LOGO), h=40),
                            # dmc.Image(src=COMPANY_LOGO, h=40),
                            dmc.Anchor(
                                children= [
                                dmc.Title("Derrick Lewis - Data Science", style={"color": "black", "textDecoration": "none"})
                                ],
                                href="/",
                            )
                        ],
                    ),
                    dmc.Group(
                        children=[
                            dmc.Button(
                                "Add/Edit Application",
                                size="md",
                                leftSection=DashIconify(icon="ic:baseline-auto-awesome-motion", width=15),
                                id='add-edit-app',
                            )
                        ],
                    ),
                ],
                h="100%",
                px="md",
            ),
        ),
        dmc.AppShellNavbar(
            id="navbar",
            children=dropdown_disc,
            p="md",
        ),
        dmc.AppShellMain(children=page_container,
                style={"marginLeft": "10vw", "marginRight": "10vw"}  # Optionally add any additional styling here
            ),
        dmc.AppShellAside("aside_", p="md"),
    ],
    header={"height": 100},
    navbar={
        "width": 300,
        "breakpoint": "sm",
        "collapsed": {"mobile": True, "desktop": True},
    },
    aside={
        "width": 2000,
        "breakpoint": "md",
        "collapsed": {"desktop": True, "mobile": True},
    },

    padding="xl",
    id="appshell",
    )
]


app.layout = dmc.MantineProvider(layout)

@callback(
    Output("appshell", "navbar"),
    Input("mobile-burger", "opened"),
    Input("desktop-burger", "opened"),
    State("appshell", "navbar"),
)
def toggle_navbar(mobile_opened, desktop_opened, navbar):
    navbar["collapsed"] = {
        "mobile": not mobile_opened,
        "desktop": not desktop_opened,
    }
    return navbar

@callback(
    Output("form_drawer", "opened"),
    Output("form_drawer", "children"),
    Input("add-edit-app", "n_clicks"),
    State("form_drawer", "opened"),
)
def toggle_aside(clicks, aside):
    if clicks is not None:
        return not aside, form_layout
    else:
        return aside, []

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)