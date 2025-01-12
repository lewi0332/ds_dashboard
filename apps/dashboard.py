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
from apps.tables import JOBcolumnDefs, defaultColDef, column_size_options, get_row_style
from plotly_theme_light import plotly_light
from main import app

# from gensim.utils import simple_preprocess
# from gensim.parsing.preprocessing import STOPWORDS
from collections import Counter
from io import BytesIO
from wordcloud import WordCloud
import base64


import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download the stopwords and punkt tokenizer if not already downloaded
nltk.download('stopwords')
nltk.download('punkt_tab')


STOPWORDS = set(stopwords.words('english')).union([
    'order',
    'food',
    'get',
    'business',
    'product',
    'team',
    'data',
    'work',
    'new',
    'needs',
    'ensure',
    'prefered',
    'strong',
    'ability',
    'years',
    'skills',
    'proven',
    ])



pio.templates["plotly_light"] = plotly_light
pio.templates.default = "plotly_light"



# Table settings
CELL_PADDING = 5
DATA_PADDING = 5
TABLE_PADDING = 1
FONTSIZE = 12


# ---------------------------------------------------------------------
# Python functions
# ---------------------------------------------------------------------

def load_data():
    client = bigquery.Client(project='dashapp-375513')
    query = """
    SELECT * FROM data_science_job_hunt.applications
    """
    query_job = client.query(query)
    dff = query_job.to_dataframe()
    dff.sort_values(by='application_date', ascending=False, inplace=True)
    return dff.to_dict('records')

def plot_wordcloud(data:pd.Series) -> BytesIO:
    freq = Counter([item for sublist in data.to_list() for item in sublist])
    wc = WordCloud(
        background_color='white',
        width=1000,
        height=500
    )
    wc.fit_words(freq)
    return wc.to_image()

def make_word_cloud_image(dff):
    img = BytesIO()
    plot_wordcloud(data=dff.tokenized).save(img, format='PNG')
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())


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
                # Job Application Tracking
                ---
                """,
                className='md')
            ])
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Markdown(
                children = """
                """,
                className='md'),
        width=5)
    ]),
# ---------------------------------------------------------------------
    dbc.Row([
        dbc.Col(html.H2('Total Applications Created',
                        style={
                            'color': 'grey',
                            'text-align': 'center',
                            'font-size': 24,
                        }),
                width=5),
        dbc.Col(html.H2('Total Rejections',
                        style={
                            'color': 'grey',
                            'font-size': 24,
                            'textAlign': 'center'
                        }),
                align="center",
                width=5)
    ],
            justify='center',
            align='center',
            style={'padding-top': 0}),
    dbc.Row([
        dbc.Col(html.H1(id='applications-created',
                        style={
                            'font-size': 36,
                            'padding': 0,
                            'textAlign': 'center',
                            'margin-bottom': 0
                        }),
                align="center",
                width=5),
        dbc.Col(html.H1(id='rejection-count',
                        style={
                            'font-size': 36,
                            'padding': 0,
                            'textAlign': 'center',
                            'margin-bottom': 0
                        }),
                align="center",
                width=5)
    ],
            justify='center'),
    html.Br(),
    dbc.Row([
        dbc.Col(html.H2('Total Responses',
                        style={
                            'color': 'grey',
                            'text-align': 'center',
                            'font-size': 24,
                        }),
                width=5),
        dbc.Col(html.H2('Total Offers',
                        style={
                            'color': 'grey',
                            'font-size': 24,
                            'textAlign': 'center'
                        }),
                align="center",
                width=5)
    ],
            justify='center',
            align='center',
            style={'padding-top': 0}),
    dbc.Row([
        dbc.Col(html.H1('N/A',
                        id='responses',
                        style={
                            'font-size': 36,
                            'padding': 0,
                            'textAlign': 'center',
                            'margin-bottom': 0
                        }),
                align="center",
                width=5),
        dbc.Col(html.H1('N/A',
                        id='offers',
                        style={
                            'font-size': 36,
                            'padding': 0,
                            'textAlign': 'center',
                            'margin-bottom': 0
                        }),
                align="center",
                width=5)
    ],
            justify='center'),
# ---------------------------------------------------------------------
    # Add modal for job details
    dbc.Modal(
        [
            dbc.ModalHeader(id="table-modal-header"),
            dbc.ModalBody(id="table-modal-body"),
            dbc.ModalFooter(
                dbc.Button("Close", id="close", className="ml-auto")
            ),
        ],
        id="table-modal",
        size="lg",
    ),
    dbc.Row([
        dbc.Col(
            [
            html.Br(),
            dag.AgGrid(
                id="datatable",
                className="ag-theme-material compact",
                # dynamically set columns
                columnDefs=JOBcolumnDefs,
                columnSize="autoSize",
                columnSizeOptions=column_size_options,
                defaultColDef=defaultColDef,
                dashGridOptions={"undoRedoCellEditing": True, 
                "cellSelection": "single",
                "rowSelection": "single"},
                getRowStyle=get_row_style,
                csvExportParams={"fileName": "job_applications.csv", "columnSeparator": ","},
                style = {'height': '500px', 'width': '100%', 'color': 'grey'}
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
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='pay-histogram')),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='sankey')),
    ]),
    dbc.Row([
        dbc.Col(
            html.Img(id='wordcloud'),
        ),
    ]),
    dbc.Row(
        dbc.Col(
                dcc.Markdown(id='codeblock',
                children = """
                ```
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
    Output('pay-histogram', 'figure'),
    Output('sankey', 'figure'),
    Input('datatable', 'rowData')
)
def update_visuals(data):
    dff = pd.DataFrame(data)
    commit_map = display_year(dff)
    pay_hist = pay_histogram(dff)
    sankey = build_sankey(dff)
    return commit_map, pay_hist, sankey

@app.callback(
    Output('applications-created', 'children'),
    Output('rejection-count', 'children'),
    Output('responses', 'children'),
    Output('offers', 'children'),
    Input('datatable', 'rowData')
)
def update_metrics(data):
    dff = pd.DataFrame(data)
    applications_created = len(dff)
    rejection_count = dff['rejection'].sum().astype(str)
    responses = dff['recruiter_screen'].sum().astype(str)
    offers = dff['offer'].sum().astype(str)
    return applications_created, rejection_count, responses, offers

# Display a field in the modal when clicked
@app.callback(
    Output("table-modal", "is_open"),
    Output("table-modal-body", "children"),
    Output("table-modal-header", "header"),
    Input("datatable", "rowData"),
    Input("datatable", "cellClicked"),
    Input("close", "n_clicks"),
    prevent_initial_call=True
)
def display_modal(data, selected_cell, n_clicks):
    if n_clicks:
        return False, [], ""
    if selected_cell:
        print(data[0])
        row = selected_cell['rowIndex']
        dff = pd.DataFrame(data)
        row_data = dff.iloc[row]
        modal_body = []
        for col in dff.columns:
            modal_body.append(dcc.Markdown(f"**{col}**: {row_data[col]}"))
        return True, modal_body, "Job Application Details"
    return False, [], ""

@app.callback(
    Output('wordcloud', 'src'),
    Input('datatable', 'rowData')
)
def update_wordcloud(data):
    dff = pd.DataFrame(data)
    # Preprocess the text data
    dff['tokenized'] = dff['requirements'].map(preprocess_text)
    # dff['tokenized'] = dff['tokenized'].apply(lambda x: [item for item in x if item.isalpha()])
    wc = make_word_cloud_image(dff)
    return wc

# ---------------------------------------------------------------------
# Python functions
# ---------------------------------------------------------------------

# Function to preprocess text
def preprocess_text(text):
    # Tokenize the text
    tokens = word_tokenize(text.lower())
    # Remove stopwords
    filtered_tokens = [word for word in tokens if word.isalnum() and word not in STOPWORDS]
    return filtered_tokens



def display_year(dff: pd.DataFrame):
    dff['application_date'] = pd.to_datetime(dff['application_date'])

    df_trunc = dff.groupby('application_date').size().reset_index(name='count')

    # Create a date spine for the last 90 days
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=180)
    date_spine = pd.DataFrame({'application_date': pd.date_range(start=start_date, end=end_date)})
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
    

    text = [str(i.date()) for i in dates_in_year] #gives something like list of strings like ‘2018-01-25’ for each date. Used in data trace to make good hovertext.
    #4cc417 green #347c17 dark green
    colorscale=[[False, '#eeeeee'], [True, '#76cf63']]
    
    fig = go.Figure(
        go.Heatmap(
            x=df_trunc['week_number'].values,
            y=df_trunc['week_day'].values,
            z=df_trunc['count'].values,
            text=text,
            hoverinfo='text',
            hovertemplate='Date: %{text}<br>Count: %{z}<extra></extra>',
            xgap=3, # this
            ygap=3, # and this is used to make the grid-like apperance
            showscale=False,
            colorscale=colorscale
        )
    )

    fig.update_layout(
        title='Activity Chart',
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


def pay_histogram(data):
    """
    Create overlaping histograms for pay_min histogram and pay_max histogram
    #TODO: Test density plot.
    """
    hist_data = data[['pay_min', 'pay_max']][(data['pay_min'] > 0) & (data['pay_max'] > 0)].astype(float)

    hist_data['pay'] = (hist_data['pay_max'] + hist_data['pay_min'])/2
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=hist_data['pay'],
            name='Pay (mean)',
            opacity=0.85,
            xbins=dict(size=5000)
        )
    )
    fig.add_trace(go.Histogram(x=hist_data['pay_min'], name='Pay Range - Min', opacity=0.2, xbins=dict(size=5000)))
    fig.add_trace(go.Histogram(x=hist_data['pay_max'], name='Pay Range - Max', opacity=0.2, xbins=dict(size=5000)))
    # Add vertical line for the mean
    fig.add_vline(
        x=hist_data['pay'].mean(),
        line_width=2,
        line_dash="dash",
        line_color="green",
        annotation_text=f"Mean Pay:<br><b>${int(hist_data['pay'].mean()):,}</b>",
        annotation_position="top right")
    # Add vertical line for the min
    fig.add_vline(
        x=hist_data['pay_min'].mean(),
        line_width=2,
        line_dash="dash",
        line_color='rgba(168, 168, 168, 0.7)',
        annotation_text=f"Range Min:<br><b>${int(hist_data['pay_min'].mean()):,}</b>",
        annotation_position="bottom right")
    # Add vertical line for the max
    fig.add_vline(
        x=hist_data['pay_max'].mean(),
        line_width=2,
        line_dash="dash",
        line_color="#19d3f3",
        #line_opacity=0.7,
        annotation_text=f"Range Max:<br><b>${int(hist_data['pay_max'].mean()):,}</b>",
        annotation_position="bottom right")
    fig.update_layout(
        title='Pay',
        xaxis_title='Pay',
        yaxis_title='Count',
        barmode='overlay',
        font={'size':10, 'color':'#9e9e9e'},

    )
    return fig


def build_sankey(data):
    """
    Create a sankey diagram to show the application journey
    """
    cold_apps = data[(data['refferal']==0)&(data['recruiter_screen']==0)&(data['rejection']==0)]['application_id'].count()
    ca_to_screen = data[(data['refferal']==0) & (data['recruiter_screen']==1)]['application_id'].count()
    ca_to_rejection = data[(data['refferal']==0) & (data['rejection']==1)]['application_id'].count()

    ref_apps = data[(data['refferal']==1)&(data['recruiter_screen']==0)&(data['rejection']==0)]['application_id'].count()
    ref_to_screen = data[(data['refferal']==1) & (data['recruiter_screen']==1)]['application_id'].count()
    ref_to_rejection = data[(data['refferal']==1) & (data['rejection']==1)]['application_id'].count()
    
    rec_apps = data[(data['recruiter']==1)&(data['recruiter_screen']==0)&(data['rejection']==0)]['application_id'].count()
    rec_to_screen = data[(data['recruiter']==1) & (data['recruiter_screen']==1)]['application_id'].count()
    rec_to_rejection = data[(data['recruiter']==1) & (data['rejection']==1)]['application_id'].count()

    screen_to_hiring_man = data[(data['recruiter_screen']==1) & (data['hiring_manager_screen']==1)]['application_id'].count()
    screen_to_rejection = data[(data['recruiter_screen']==1) & (data['hiring_manager_screen']==0) & (data['rejection']==1)]['application_id'].count()
    screen_to_no_response = data[(data['recruiter_screen']==1) & (data['hiring_manager_screen']==0) & (data['rejection']==0)]['application_id'].count()

    hiring_to_tech = data[(data['hiring_manager_screen']==1) & (data['technical_screen']==1)]['application_id'].count()
    hiring_to_rejection = data[(data['hiring_manager_screen']==1) & (data['technical_screen']==0) & (data['rejection']==1)]['application_id'].count()
    hiring_to_no_response = data[(data['hiring_manager_screen']==1) & (data['technical_screen']==0) & (data['rejection']==0)]['application_id'].count()

    tech_to_offer = data[(data['technical_screen']==1) & (data['offer']==1)]['application_id'].count().astype(int)
    tech_to_rejection = data[(data['technical_screen']==1) & (data['offer']==0) & (data['rejection']==1)]['application_id'].count()
    tech_to_no_response = data[(data['technical_screen']==1) & (data['offer']==0) & (data['rejection']==0)]['application_id'].count()

    fig = go.Figure(data=[go.Sankey(
        node = dict(
            hovertemplate='%{label}:<br></b>%{value:0}<extra></extra>',
            pad = 15,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            label = [
                'Cold Application',
                'Network Refferal',
                'Recruiter Initiated',
                'Recruiter Screen',
                'Hiring Manager Screen',
                'Technical Screen',
                'No Response',
                'Rejection',
                'Offer'],
            ),
        link = dict(
            source = [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5],
            target = [3, 6, 7, 3, 6, 7, 3, 6, 7, 4, 6, 7, 5, 6, 7, 6, 7, 8],
            value = [
                ca_to_screen,
                cold_apps,
                ca_to_rejection,
                ref_to_screen,
                ref_apps,
                ref_to_rejection,
                rec_to_screen,
                rec_apps,
                rec_to_rejection,
                screen_to_hiring_man,
                screen_to_rejection,
                screen_to_no_response,
                hiring_to_tech,
                hiring_to_rejection,
                hiring_to_no_response,
                tech_to_offer,
                tech_to_rejection,
                tech_to_no_response
                ],
            hovertemplate='%{source.label} -> %{target.label}: %{value:0}<extra></extra>',
            )
        )])

    fig.update_layout(
        title_text="Application Journey (Sankey Diagram)",
        title_font_size=10,
        title_font_color='#9e9e9e',
        )
    return fig
