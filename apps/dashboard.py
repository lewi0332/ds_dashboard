"""


Author: Derrick Lewis
"""
import json
from datetime import datetime, timedelta, date
import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import dash_mantine_components as dmc
from dash import dcc, html, register_page, callback
from dash.dependencies import Input, Output
import dash_ag_grid as dag
from google.cloud import bigquery
from apps.tables import JOBcolumnDefs, defaultColDef, column_size_options, get_row_style
from plotly_theme_light import plotly_light

# from gensim.utils import simple_preprocess
# from gensim.parsing.preprocessing import STOPWORDS
from collections import Counter
from io import BytesIO
from wordcloud import WordCloud
import base64


import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


register_page(__name__)

# Download the stopwords and punkt tokenizer if not already downloaded
nltk.download('stopwords', quiet=True)
nltk.download('punkt_tab', quiet=True)


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
    query_job = client.query_and_wait(query)
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

layout = dmc.Container(
    children = [
        dcc.Store(id='initial-data', data=load_data()),
        dcc.Markdown(
            children = """
            ---
            # Job Application Tracking
            ---
            """,
            className='card-text'
        ),
    # ---------------------------------------------------------------------
        dmc.Grid(
            children = [
                dmc.GridCol(
                    html.H2('Total Applications Created',
                            style={'color': 'grey',
                                'text-align': 'center',
                                'font-size': 24
                                }
                    ),
                    span=6
                ),
                dmc.GridCol(
                    html.H2('Total Rejections',
                            style={
                                'color': 'grey',
                                'font-size': 24,
                                'textAlign': 'center'
                                }
                    ),
                    span=6
                )
            ],
        ),
        dmc.Grid(
            children = [
                dmc.GridCol(
                    html.H1(id='applications-created',
                            style={
                                'font-size': 36,
                                'padding': 0,
                                'textAlign': 'center',
                                'margin-bottom': 0
                            }
                    ),
                    span=6
                ),
                dmc.GridCol(
                    html.H1(id='rejection-count',
                            style={
                                'font-size': 36,
                                'padding': 0,
                                'textAlign': 'center',
                                'margin-bottom': 0
                            }
                    ),
                    span=6
                )
            ],
            justify='center'
        ),
        html.Br(),
        dmc.Grid(
            children = [
                dmc.GridCol(
                    html.H2('Total Responses',
                            style={
                                'color': 'grey',
                                'text-align': 'center',
                                'font-size': 24,
                            }
                    ),
                    span=6
                ),
                dmc.GridCol(
                    html.H2('Total Offers',
                            style={
                                'color': 'grey',
                                'font-size': 24,
                                'textAlign': 'center'
                            }
                    ),
                    span=6
                )
            ],
            justify='center',
            align='center',
            style={'padding-top': 0}
        ),
        dmc.Grid(
            children = [
                dmc.GridCol(
                    html.H1('N/A',
                            id='responses',
                            style={
                                'font-size': 36,
                                'padding': 0,
                                'textAlign': 'center',
                                'margin-bottom': 0
                            }
                    ),
                    span=6
                ),
                dmc.GridCol(
                    html.H1('N/A',
                            id='offers',
                            style={
                                'font-size': 36,
                                'padding': 0,
                                'textAlign': 'center',
                                'margin-bottom': 0
                            }
                    ),
                    span=6
                )
            ],
            justify='center'),
    # ---------------------------------------------------------------------
        # Add modal for job details
        dmc.Modal(
            id="table-modal",
            size="55%",
            centered=True,
            children=[
                dcc.Markdown(id='modal-body'),
                dmc.Button("Close", id="close", className="ml-auto")
            ],
        ),
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
        html.Br(),
        dmc.Button('Reload', id='reloadTop', n_clicks=0),
        html.Br(),
        html.Hr(),
        dcc.Markdown(id='intro',
                    children = """
                    ---
                    ### Visualizations
                    """,
                    className='md'),
        dcc.Graph(id='commit-map'),
        dmc.Grid(
            children = [
                dmc.GridCol(
                    dcc.Graph(id='pay-histogram'),
                    span=6
                ),
                dmc.GridCol(
                    dcc.Graph(id='box-plots'),
                    span=6
                )
            ],
        ),
        dcc.Graph(id='sankey'),
        
        dmc.Group([
            # Center this column
            dmc.Stack(
                html.Img(id='wordcloud')
                ),
        ], justify="center"),
        dmc.Group(
            dmc.Stack(
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
],
fluid=True
)

# ---------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------

@callback(
    Output("datatable", "rowData"),
    Input("initial-data", "data"),
    Input("reloadTop", "n_clicks")
)
def load_initial_data(data, n_clicks):
    if n_clicks > 0:
        data = load_data()
    return data

# update Main visualizations
@callback(
    Output('commit-map', 'figure'),
    Output('pay-histogram', 'figure'),
    Output('sankey', 'figure'),
    Output('box-plots', 'figure'),
    Input('datatable', 'virtualRowData'),
    prevent_initial_call=True
)
def update_visuals(data):
    if len(data) == 0:
        return go.Figure(), go.Figure(), go.Figure(), go.Figure()
    dff = pd.DataFrame(data)
    commit_map = display_year(dff)
    pay_hist = pay_histogram(dff)
    sankey = build_sankey(dff)
    box_plots = build_box_plots(dff)
    return commit_map, pay_hist, sankey, box_plots

@callback(
    Output('applications-created', 'children'),
    Output('rejection-count', 'children'),
    Output('responses', 'children'),
    Output('offers', 'children'),
    Input('datatable', 'rowData'),
    prevent_initial_call=True
)
def update_metrics(data):
    if len(data) == 0:
        return 'N/A', 'N/A', 'N/A', 'N/A'
    dff = pd.DataFrame(data)
    applications_created = len(dff)
    rejection_count = dff['rejection'].sum().astype(str)
    straight_rejections = dff[dff['recruiter_screen']==0]['rejection'].sum()
    responses = str(dff['recruiter_screen'].sum() + straight_rejections)
    offers = dff['offer'].sum().astype(str)
    return applications_created, rejection_count, responses, offers

# Display a field in the modal when clicked
@callback(
    Output("table-modal", "opened"),
    Output("modal-body", "children"),
    Output("table-modal", "title"),
    Input("datatable", "virtualRowData"),
    Input("datatable", "cellClicked"),
    Input("close", "n_clicks"),
    prevent_initial_call=True
)
def display_modal(data, selected_cell, n_clicks):
    if n_clicks:
        return False, [], ""
    if selected_cell:
        row = selected_cell['rowIndex']
        dff = pd.DataFrame(data)
        row_data = dff.iloc[row]
        modal_body = ""
        for col in dff.columns:
            modal_body += f"###### {col}: \n {row_data[col]}\n"
        return True, modal_body, "Job Application Details"
    return False, "", ""

@callback(
    Output('wordcloud', 'src'),
    Input('datatable', 'virtualRowData'),
    prevent_initial_call=True
)
def update_wordcloud(data):
    if len(data) == 0:
        return 'na'
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
    """
    hist_data = data[['pay_min', 'pay_max', 'company_name']][(data['pay_min'] > 0) & (data['pay_max'] > 0)]
    hist_data[['pay_min', 'pay_max']] = hist_data[['pay_min', 'pay_max']].astype(float)

    hist_data['pay'] = (hist_data['pay_max'] + hist_data['pay_min'])/2


    # Calculate the KDE
    kde = gaussian_kde(hist_data['pay'])
    x_vals = np.linspace(min(hist_data['pay']), max(hist_data['pay']), 100)
    y_vals = kde(x_vals)

    # convert y_vals to a the frequency scale of hist_data['pay']
    y_vals = y_vals*hist_data['pay'].mean()

    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=hist_data['pay'],
            name='Pay (mean)',
            opacity=0.85,
            xbins=dict(size=5000),
        )
    )
    fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name='KDE', line=dict(width=2)))
    # fig.add_trace(go.Histogram(x=hist_data['pay_min'], name='Pay Range - Min', opacity=0.2, xbins=dict(size=5000)))
    # fig.add_trace(go.Histogram(x=hist_data['pay_max'], name='Pay Range - Max', opacity=0.2, xbins=dict(size=5000)))
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
        line_color='rgba(168, 168, 168, 0.6)',
        annotation_text=f"Range Min:<br><b>${int(hist_data['pay_min'].mean()):,}</b>",
        annotation_position="bottom right")
    # Add vertical line for the max
    fig.add_vline(
        x=hist_data['pay_max'].mean(),
        line_width=2,
        line_dash="dash",
        line_color='rgba(25, 211, 243, 0.6)',
        # line_opacity=0.7,
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
    cold_apps = data[(data['refferal']==0) & (data['recruiter']==0) & (data['recruiter_screen']==0)&(data['rejection']==0)]['application_id'].count()
    ca_to_screen = data[(data['refferal']==0) & (data['recruiter']==0) & (data['recruiter_screen']==1)]['application_id'].count()
    ca_to_rejection = data[(data['refferal']==0) & (data['recruiter']==0) & (data['rejection']==1)]['application_id'].count()

    ref_apps = data[(data['refferal']==1)  & (data['recruiter_screen']==0)&(data['rejection']==0)]['application_id'].count()
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
                'Cold Application', # 0
                'Network Refferal', # 1
                'Recruiter Initiated', # 2
                'Recruiter Screen', # 3
                'Hiring Manager Screen', # 4
                'Technical Screen', # 5
                'No Response', # 6
                'Rejection', # 7
                'Offer'], # 8
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
                screen_to_no_response,
                screen_to_rejection,
                hiring_to_tech,
                hiring_to_no_response,
                hiring_to_rejection,
                tech_to_no_response,
                tech_to_rejection,
                tech_to_offer,
                ],
            hovertemplate='%{source.label} -> %{target.label}: %{value:0}<extra></extra>',
            )
        )])

    fig.update_layout(
        title_text="Application Journey (Sankey Diagram)",
        # title_font_size=10,
        title_font_color='#9e9e9e',
        )
    return fig


def build_box_plots(data: pd.DataFrame) -> go.Figure:
    """
    Build a box plot to show the distribution of pay by office participation

    Args:
    -----
    data: pd.DataFrame
        The data to use to build the box plot - must contain the columns 'pay_min', 'pay_max', and 'office_participation'

    Returns:
    --------
    fig: go.Figure
        The box plot figure
    """
    data['pay_mean'] = (data['pay_min'] + data['pay_max'])/2

    data.dropna(subset=['office_participation'], inplace=True)
    data.dropna(subset=['pay_mean'], inplace=True)
    data = data[data['pay_mean'] > 0]

    remote = data['pay_mean'][data['office_participation']=='Remote']
    hybrid = data['pay_mean'][data['office_participation']=='Hybrid']
    office = data['pay_mean'][data['office_participation']=='On-site']

    fig = go.Figure()
    fig.add_trace(go.Box(y=remote, name='Remote'))
    fig.add_trace(go.Box(y=hybrid, name='Hybrid'))
    fig.add_trace(go.Box(y=office, name='On Site'))
    fig.update_layout(
        title='Pay Distribution by Office Participation',
        xaxis_title='Category',
        yaxis_title='Mean Salary',
        boxmode='group',
        font={'size':10, 'color':'#9e9e9e'}
        )
    return fig