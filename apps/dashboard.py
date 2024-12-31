"""


Author: Derrick Lewis
"""
import json
from datetime import datetime, timedelta, date
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_ag_grid as dag
from google.cloud import bigquery
from apps.tables import JOBcolumnDefs, defaultColDef
from plotly_theme_light import plotly_light
from main import app

pio.templates["plotly_light"] = plotly_light
pio.templates.default = "plotly_light"

client = bigquery.Client(project='dashapp-375513')

# Table settings
CELL_PADDING = 5
DATA_PADDING = 5
TABLE_PADDING = 1
FONTSIZE = 12


# ---------------------------------------------------------------------
# Python functions
# ---------------------------------------------------------------------

def load_data():
    dff = pd.read_parquet("gs://dashapp-375513.appspot.com/data.parquet")
    return dff.to_dict('records')


# ---------------------------------------------------------------------
# Create app layout
# ---------------------------------------------------------------------

layout = dbc.Container([
    dcc.Store(id='initial-data', data=load_data()),
    dbc.Row([
        dbc.Col(
            [
                dcc.Markdown(id='intro',
                children = """
                ---
                # Job Applications Tracking
                ---
                
                Volume of job applications I have applied to.
    
                ---
                """,
                className='md')
            ])
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Markdown(
                children = """
                ---
                ### Info
                """,
                className='md'),
        width=5)
    ]),
    dbc.Row([
        dbc.Col(
            [
            html.Br(),
            dag.AgGrid(
                id="datatable",
                className="ag-theme-material",
                # dynamically set columns
                columnDefs=JOBcolumnDefs,
                columnSize="autoSize",
                defaultColDef=defaultColDef,
                dashGridOptions={"undoRedoCellEditing": True, 
                "cellSelection": "single",
                "rowSelection": "single"},
                csvExportParams={"fileName": "job_applications.csv", "columnSeparator": ","},
                style = {'height': '400px', 'width': '100%', 'color': 'grey'}
                ),
            dbc.Button(
                'Reload', id='reloadTop', n_clicks=0,
                className='download-button-style'
                    ),
            ]
        ),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dcc.Markdown(id='intro',
                children = """
                ---
                ### Visualizations
                """,
                className='md')
        ),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='commit-map')),
        # dbc.Col(
        #     dcc.Graph(id='scatter'), width=6)
    ]),
    dbc.Row(
        dbc.Col(
                dcc.Markdown(id='codeblock',
                children = """
                ```sql
                CREATE SCHEMA 
                );
                ```
                """,
                
                className='md')
            ),
        style={"maxHeight": "400px", "overflow": "scroll"}
    ),
    html.Br(),
])

# ---------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------

@app.callback(
    Output("datatable", "rowData"),
    Input("initial-data", "data"),
    Input("reloadTop", "n_clicks")
)
def load_initial_data(data, n_clicks):
    if n_clicks > 0:
        data = load_data()
    return data

# update commit map
@app.callback(
    Output('commit-map', 'figure'),
    Input('datatable', 'rowData')
)
def update_commit_map(data):
    dff = pd.DataFrame(data)
    
    fig = display_year(dff)
    return fig


def display_year(dff: pd.DataFrame):
    dff['application_date'] = pd.to_datetime(dff['application_date'])

    df_trunc = dff.groupby('application_date').size().reset_index(name='count')

    # Create a date spine for the last 90 days
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=180)
    date_spine = pd.DataFrame({'application_date': pd.date_range(start=start_date, end=end_date).date})
    date_spine['application_date'] = pd.to_datetime(date_spine['application_date'])
    date_spine['week_day'] = date_spine['application_date'].dt.weekday

    # drop rows up to the very first Monday, keep  all days from Monday on
    # This allows the week_numbers to start cleanly from 1
    first_weekday = date_spine.loc[0].week_day
    date_spine = date_spine.iloc[7-first_weekday:]
    date_spine.reset_index(drop=True, inplace=True)
    
    # build fake weeknumbers starting from 1 and incrementing by 1 for each week
    date_spine['week_number'] = date_spine.index // 7 + 1

    # Merge the data with the date spine
    df_trunc = date_spine.merge(df_trunc, on='application_date', how='left').fillna(0)
    start_date = date_spine.application_date.min()
    end_date = date_spine.application_date.max()

    delta = end_date-start_date

    # Create a list of month names, days in month, and month positions in df_trunc

    month_names = df_trunc['application_date'].dt.month_name().unique()
    # Get the number of days in each month
    month_days = df_trunc.groupby(df_trunc['application_date'].dt.month)['application_date'].count().values.tolist()
    month_positions = (np.cumsum(month_days) - 15)/7
    dates_in_year = [start_date + timedelta(i) for i in range(delta.days+1)] # list with datetimes for each day a year
    

    text = [str(i) for i in dates_in_year] #gives something like list of strings like ‘2018-01-25’ for each date. Used in data trace to make good hovertext.
    #4cc417 green #347c17 dark green
    colorscale=[[False, '#eeeeee'], [True, '#76cf63']]
    
    fig = go.Figure(
        go.Heatmap(
            x=df_trunc['week_number'].values,
            y=df_trunc['week_day'].values,
            z=df_trunc['count'].values,
            text=text,
            hoverinfo='text',
            xgap=3, # this
            ygap=3, # and this is used to make the grid-like apperance
            showscale=False,
            colorscale=colorscale
        )
    )

    fig.update_layout(
        title='activity chart',
        height=250,
        yaxis=dict(
            showline=False, showgrid=False, zeroline=False,
            tickmode='array',
            ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            tickvals=[0, 1, 2, 3, 4, 5, 6],
            autorange="reversed",
        ),
        xaxis=dict(
            showline=False, showgrid=False, zeroline=False,
            tickmode='array',
            ticktext=month_names,
            tickvals=month_positions,
        ),
        font={'size':10, 'color':'#9e9e9e'},
        plot_bgcolor=('#fff'),
        margin = dict(t=40),
        showlegend=False,
    )
    return fig