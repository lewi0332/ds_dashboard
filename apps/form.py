import time
from datetime import date
import pandas as pd
import dash_daq as daq
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, ctx
from google.cloud import bigquery
from main import app
from data.datamodel import Application, application_form_fields
from apps.utils import (
    access_secret_version,
    upload_options_to_gcs,
    read_options_from_gcs,
    upsert_data_to_bigQuery_table)

VALID_USERNAME_PASSWORD_PAIRS = access_secret_version("dashapp-375513", "VALID_USERNAME_PASSWORD_PAIRS", "latest", json_type=True)

BUCKET_NAME = access_secret_version(
    "dashapp-375513",
    "BUCKET_NAME",
    "latest")

# Layout of the app
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Job Application Create / Update Form"),
            html.Hr(),
        ])
    ]),
    # Add button to load current data
    dbc.Row([
        dbc.Col([
            dbc.Label("Select a Current Application to Edit"),
            dcc.Dropdown(
                id='current-application-dropdown',
                multi=False
            ),
        ], width=6),
        dbc.Col([
            html.Br(),
            dbc.Button("Edit Application", id="load-application-button", class_name='view-page-button-style',),
        ], width=2),
        dbc.Col([
            html.Br(),
            dbc.Button("Start New Application", id="new-button", class_name='view-page-button-style' ),
            html.Div(id="load-output-message", className="mt-3"),    
            html.Div(id="new-output-message", className="mt-3")
        ]),
        dbc.Col(width=1),
    ]),
    html.Hr(),
    dbc.Row([
        dbc.Col([
            dbc.Button("Reload Current Data", id="load-button", class_name='view-page-button-style', n_clicks=0,  style = dict(display='none')),
        ], width=3),
        dbc.Col(
            width=3),
    ]),
    html.H3("Role Information"),
    dbc.Row([
        dbc.Col([
            dbc.Form([
                dbc.Label("Application ID"),
                dbc.Input(type="text", id="application-id", placeholder="Enter Application ID"),
                dbc.Label("Date"),
                dcc.DatePickerSingle(id='application-date',
                    min_date_allowed=date(2024, 12, 1),
                    max_date_allowed=date(2026, 1, 1),
                    initial_visible_month=date.today(),
                    date=date.today()
                ),
                dbc.Label("Application Link"),
                dbc.Input(type="text", id="application-link", placeholder="Enter Application Link"),
                dbc.Label("Company"),
                dbc.Input(type="text", id="company-input", placeholder="Enter Company name"),
                dbc.Label("Job Title"),
                dbc.Input(type="text", id="job-title-input", placeholder="Enter Job title"),
                dbc.Label("Location"),
                dbc.Input(type="text", id="location-input", placeholder="Enter Company Location"),
                dbc.Label("Office Participation"),
                dcc.Dropdown(['Hybrid', 'Remote', 'On-site'], 'Hybrid', id='office-participation-dropdown'),
                dbc.Label("Role Description"),
                dbc.Textarea(id="role-desc-input", placeholder="Enter description of role", style={'width': '100%', 'height': 300}),
                dbc.Label("Responsibilities"),
                dbc.Textarea(id="responsibilities-input", placeholder="Enter responsibilities of the Role", style={'width': '100%', 'height': 300}),
                dbc.Label("Requirements"),
                dbc.Textarea( id="requirements-input", placeholder="Enter Requirements of the Role", style={'width': '100%', 'height': 300}),
                dbc.Label("Pay Min"),
                dbc.Input(type="number", id="pay-min-input", placeholder="Enter Minimum Salary of the Role"),
                dbc.Label("Pay Max"),
                dbc.Input(type="number", id="pay-max-input", placeholder="Enter Maximum Salary of the Role"),
                dbc.Label("CV version"),
                dbc.Input(type="text", id="cv-version-input", placeholder="Enter the name of the CV"),
                dbc.Label("Cover Letter version"),
                dbc.Input(type="text", id="cover-letter-input", placeholder="Enter the name of the cover letter"),
            ])
        ], width=10),
    ]),
    html.Hr(),
    html.H3("Skill Assessment"),
    dbc.Row([
        dbc.Col([
            dbc.Label("Self Assessment"),
            dbc.Label("How confident do I feel about my capabilities in this role? (0 - 100)", style={'font-size': '1rem'}),
            dcc.Slider(0, 100, 5,
               value=50,
               id='self-assessment-slider'),
        ]),
        dbc.Col([
            dbc.Label("Core Skills"),
            dcc.Dropdown(read_options_from_gcs(BUCKET_NAME, "core_skills_list.json"),
                ['python', 'pandas', 'sql'],
                multi=True,
                id='core-skills-dropdown',
            ),
            dbc.Input(type="text", id="new-core-skill-input", placeholder="Enter new core skill", size="sm", debounce=True),
        ]),
    dbc.Row([
        dbc.Col([
            dbc.Label("LLM Focus"),
            daq.BooleanSwitch(id='llm-switch', on=False, style={'float': 'left'})
        ]),
        dbc.Col([
            dbc.Label("MMM Focus"),
            daq.BooleanSwitch(id='mmm-switch', on=False, style={'float': 'left'}),
        ]),
    ]),
    dbc.Row([    
        dbc.Col([
            dbc.Label("Marketing Focus"),
            daq.BooleanSwitch(id='marketing-switch', on=False, style={'float': 'left'}),
        ]),
        dbc.Col([
            dbc.Label("Retail Focus"),
            daq.BooleanSwitch(id='retail-switch', on=False, style={'float': 'left'}),
        ]),
    ]),
        dbc.Row([    
        dbc.Col([
            dbc.Label("Healthcare Focus"),
            daq.BooleanSwitch(id='healthcare-switch', on=False, style={'float': 'left'}),
        ]),
        dbc.Col([
            dbc.Label("Finance Focus"),
            daq.BooleanSwitch(id='finance-switch', on=False, style={'float': 'left'}),
        ]),
    ]),
    dbc.Row([    
        dbc.Col([
            dbc.Label("Senior Role"),
            daq.BooleanSwitch(id='senior-role-switch', on=False, style={'float': 'left'}),
        ]),
        dbc.Col([
            dbc.Label("Staff Role"),
            daq.BooleanSwitch(id='staff-role-switch', on=False, style={'float': 'left'}),
        ]),
    ]),
    dbc.Row([    
        dbc.Col([
            dbc.Label("Generalist Role"),
            daq.BooleanSwitch(id='generalist-switch', on=False, style={'float': 'left'}),
        ]),
        dbc.Col([
            dbc.Label("Management Role"),
            daq.BooleanSwitch(id='management-switch', on=False, style={'float': 'left'}),
        ]),
    ]),
    
    html.Hr(),
    html.H3("Source of Application"),
    dbc.Row([    
        dbc.Col([
            dbc.Label("Personal Refferal"),
            daq.BooleanSwitch(id='refferal-switch', on=False, style={'float': 'left'}),
        ]),
        dbc.Col([
            dbc.Label("Recruiter Initiated"),
            daq.BooleanSwitch(id='recruiter-switch', on=False, style={'float': 'left'}),
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Label("Application Source"),
            dcc.Dropdown(read_options_from_gcs(BUCKET_NAME, "application_source_list.json"),
                # options= ['Indeed', 'Glassdoor', 'Monster', 'LinkedIn', 'BuiltIn', 'Company Website'],
                value= 'LinkedIn',
                id='app-source-dropdown',
            ),
            dbc.Input(type="text", id="new-app-source-input", placeholder="Enter new source", size="sm", debounce=True),
        ]),
    ]),
    html.Hr(),
    html.H3("Application Progress"),
    dbc.Row([
        dbc.Col([
                dbc.Label("Response - Recruiter Screen"),
                daq.BooleanSwitch(id='recruiter-screen-switch', on=False, style={'float': 'left'}),
        ]),
        dbc.Col([
                dbc.Label("Response - Recruiter Screen - Date"),
                dcc.DatePickerSingle(id='recruiter-screen-date',
                    min_date_allowed=date(2024, 12, 1),
                    max_date_allowed=date(2026, 1, 1),
                    initial_visible_month=date.today(),
                    date=None
                ),
        ]),
    ]),
    dbc.Row([
        dbc.Col([
                dbc.Label("Response - Hiring Manager Screen"),
                daq.BooleanSwitch(id='hiring-manager-screen-switch', on=False, style={'float': 'left'}),
        ]),
        dbc.Col([
                dbc.Label("Response - Hiring Manager Screen - Date"),
                dcc.DatePickerSingle(id='hiring-manager-screen-date',
                    min_date_allowed=date(2024, 12, 1),
                    max_date_allowed=date(2026, 1, 1),
                    initial_visible_month=date.today(),
                    date=None
                ),
        ]),
    ]),
    dbc.Row([
        dbc.Col([
                dbc.Label("Response - Technical Screen / Test / Assignment"),
                daq.BooleanSwitch(id='technical-screen-switch', on=False, style={'float': 'left'}),
        ]),
        dbc.Col([
                dbc.Label("Response - Technical Screen - Date"),
                dcc.DatePickerSingle(id='technical-screen-date',
                    min_date_allowed=date(2024, 12, 1),
                    max_date_allowed=date(2026, 1, 1),
                    initial_visible_month=date.today(),
                    date=None
                ),
        ]),
    ]),
    dbc.Row([
        dbc.Col([
                dbc.Label("Technical Screen Type"),
                dcc.Dropdown(['Interview', 'Test', 'Task'], id='technical-screen-type'),
        ]),
        dbc.Col([
                dbc.Label("Time Spent - Technical Screen"),
                dbc.Input(type="number", id="technical-screen-time", placeholder="Enter time spent on the technical screen in minutes"),
        ]),
    ]),
    dbc.Row([
        dbc.Col([
                dbc.Label("Offer"),
                #Set the style of this switch to position on the left of the column
                daq.BooleanSwitch(id='offer-switch', on=False, style={'float': 'left'}),
        ]),
        dbc.Col([
                dbc.Label("Offer - Date"),
                dcc.DatePickerSingle(id='offer-date',
                    min_date_allowed=date(2024, 12, 1),
                    max_date_allowed=date(2026, 1, 1),
                    initial_visible_month=None,
                    date=None
                ),
        ]),
    ]),
    dbc.Row([
        dbc.Col([
                dbc.Label("Rejection"),
                daq.BooleanSwitch(id='rejection-switch', on=False, style={'float': 'left'}),
        ]),
        dbc.Col([
                dbc.Label("Rejection - Date"),
                dcc.DatePickerSingle(id='rejection-date',
                    min_date_allowed=date(2024, 12, 1),
                    max_date_allowed=date(2026, 1, 1),
                    initial_visible_month=date.today(),
                    date=None
                ),
        ]),
    ], className="mb-5"),
    dbc.Row([
        dbc.Col([
                dbc.Button("Submit", id="submit-button", class_name='view-page-button-style',),
        ]),
        dbc.Col([
                dbc.Button("Delete", id="delete-button", class_name='view-page-button-style',),
        ]),
        dbc.Col([
            dcc.Loading(id='loading_icon',
                    children=[
                        html.Div(id="output-message", className="mt-3")
                    ],
                    type='default'
                ),
        ]),
        dbc.Col(width=2),
    ]),
    dcc.Store(id="current-application-store", data=None),
    dbc.Modal(
        [
            dbc.ModalHeader("Login"),
            dbc.ModalBody([
                dbc.Input(id='username', placeholder='Username', type='text'),
                dbc.Input(id='password', placeholder='Password', type='password'),
                dbc.Button('Login', id='login-button', color='primary', className='view-page-button-style')
            ]),
            dbc.ModalFooter(
                dbc.Button("Close", id="close", className='view-page-button-style')
            ),
        ],
        id="modal",
        is_open=False,
    ),
    # Add an "are you sure" modal
    dbc.Modal(
        [
            dbc.ModalHeader("Delete Application"),
            dbc.ModalBody("Are you sure you want to delete this application?"),
            dbc.ModalFooter([
                dbc.Button("Delete", id="delete-confirmed", className="ml-auto", class_name='view-page-button-style',),
                dbc.Button("Cancel", id="delete-cancel", className='view-page-button-style')
            ]),
        ],
        id="delete-modal",
        is_open=False
        )
    ])
])




# Custom authentication check
def is_authenticated(username, password):
    return VALID_USERNAME_PASSWORD_PAIRS.get(username) == password

# Callback to handle form submission
@app.callback(
    Output("output-message", "children", allow_duplicate=True),
    Output('modal', 'is_open'),
    Output("load-button", "n_clicks"),
    Input("submit-button", "n_clicks"),
    Input('login-button', 'n_clicks'),
    Input('close', 'n_clicks'),
    State('username', 'value'),
    State('password', 'value'),
    State('modal', 'is_open'),
    [State(i[0], i[1]) for i in application_form_fields],
    prevent_initial_call=True
)
def update_bigquery(submit_n_clicks,
                    login_n_clicks,
                    close_n_clicks,
                    username,
                    password,
                    is_open,
                    *args):
    
    # Extract the dynamically passed arguments
    raw_data = args[:len(application_form_fields)]

    button_id = dash.callback_context
    button_id = button_id.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'submit-button':
        if username and password and is_authenticated(username, password):
            print(raw_data)
            # Extract the values from the form and create an Application object
            app = Application(
                application_id = raw_data[0],
                application_date = raw_data[1],
                application_link = raw_data[2],
                company_name = raw_data[3],
                job_title = raw_data[4],
                location = raw_data[5],
                office_participation = raw_data[6],
                role_desc = raw_data[7],
                responsibilities = raw_data[8],
                requirements = raw_data[9],
                pay_min = raw_data[10],
                pay_max = raw_data[11],
                cv_version = raw_data[12],
                cover_letter = raw_data[13],
                self_assessment = raw_data[14],
                core_skills = raw_data[15],
                llm = raw_data[16],
                mmm = raw_data[17],
                marketing = raw_data[18],
                retail = raw_data[19],
                healthcare = raw_data[20],
                finance = raw_data[21],
                senior_role = raw_data[22],
                staff_role = raw_data[23],
                generalist_role = raw_data[24],
                management_role = raw_data[25],
                refferal = raw_data[26],
                recruiter = raw_data[27],
                app_source = raw_data[28],
                recruiter_screen = raw_data[29],
                recruiter_screen_date = raw_data[30],
                hiring_manager_screen = raw_data[31],
                hiring_manager_screen_date = raw_data[32],
                technical_screen = raw_data[33],
                technical_screen_date = raw_data[34],
                technical_screen_type = raw_data[35],
                technical_screen_time = raw_data[36],
                offer = raw_data[37],
                offer_date = raw_data[38],
                rejection = raw_data[39],
                rejection_date = raw_data[40]
            )
            
            job = upsert_data_to_bigQuery_table(app)
            job.result()
            errors = job.errors

            if errors == [] or errors is None:
                return f"Application {app.application_id} submitted successfully.", False, 1
            else:
                return f"Encountered errors while inserting rows in Bigquery: {errors}", False, None
        else:
            return "Opening login modal", True, None
    elif button_id == 'login-button':
        if is_authenticated(username, password):
            return "Authenticated", False, None
        else:
            time.sleep(2)
            return "Authentication failed", True, None
    elif button_id == 'close':
        return "", False, None
    return "", is_open


# Callback to load current data
@app.callback(
    Output("load-output-message", "children"),
    Output("current-application-dropdown", "options"),
    Output("current-application-dropdown", "value"),
    Output("current-application-store", "data"),
    Input("load-button", "n_clicks")
)
def load_data(n_clicks):
    """
    Load the data from BigQuery and return the options for the dropdown

    Store data in a hidden div to be used later
    """
    if n_clicks is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    client = bigquery.Client()
    query = """
    SELECT
        application_id,
        company_name,
        job_title
    FROM `dashapp-375513.data_science_job_hunt.applications`
    """
    dff = client.query(query).to_dataframe()
    if dff.empty:
        return "No data available.", [], None, None
    dff[['application_id', 'company_name', 'job_title']] = dff[['application_id', 'company_name', 'job_title']].fillna('').astype(str)
    # Get the options for the dropdown
    options = [{"label": row['company_name'] +' - ' + row['job_title'], "value": row["application_id"]} for index, row in dff.iterrows()]
    return "Data loaded successfully.", options, options[0]["value"], dff.to_dict("records")


# Callback to load the selected application
@app.callback(
    [Output(i[0], i[1]) for i in application_form_fields],
    Input("load-application-button", "n_clicks"),
    Input("new-button", "n_clicks"),
    State("current-application-dropdown", "value"),
    State("current-application-store", "data"),
    prevent_initial_call=True
)
def load_application(edit_clicks, new_clicks, application_id, raw_data):
    if edit_clicks is None and new_clicks is None:
        return dash.no_update
    triggered_id = ctx.triggered_id
    if triggered_id == 'new-button':
        dff = pd.DataFrame(raw_data)
        dff['application_id'] = dff['application_id'].astype(int)
        new_id = dff['application_id'].max() + 1
        new_app = Application(application_id = str(new_id), company_name = 'Enter Company Name', job_title = 'Job Title')
        
        # get a tuple of the default values
        new_app = tuple(new_app.model_dump().values())
        
        return new_app
    
    elif triggered_id == 'load-application-button':
        # Load the record form bigquery where application_id = application_id store it as an Application object

        client = bigquery.Client()
        query = f"""
        SELECT * FROM `dashapp-375513.data_science_job_hunt.applications` WHERE application_id = '{application_id}'
        """
        # bigquery_data = client.query(query).to_dataframe()
        query_job = client.query(query)  # API request
        rows = query_job.result()
        
        # store the data in a tuple
        row = list(rows)[0]
        row = dict(row)
        row['core_skills'] = [row['core_skills']['list'][i]['element'] for i in range(len(row['core_skills']['list']))]

        row.values()

        # Remove the created_at and updated_at fields
        row.pop('created_at')
        row.pop('updated_at')

        return [row[i[2]] for i in application_form_fields]


# Add a delete button to delete the selected application with confirmation modal
@app.callback(
    Output("delete-modal", "is_open"),
    Output("output-message", "children", allow_duplicate=True),
    Output('modal', 'is_open', allow_duplicate=True),
    Output("load-button", "n_clicks", allow_duplicate=True),
    Input("delete-button", "n_clicks"),
    Input("delete-confirmed", "n_clicks"),
    State("delete-modal", "is_open"),
    State("current-application-dropdown", "value"),
    State("current-application-store", "data"),
    State("username", "value"),
    State("password", "value"),
    prevent_initial_call=True
)
def handle_delete_modal(delete_clicks, delete_confirmed_clicks, is_open, application_id, raw_data, username, password):
    """
    Toggle the delete confirmation modal and delete the selected application.
    """
    if delete_clicks is None and delete_confirmed_clicks is None:
        return False, dash.no_update, False, None
    if username and password and is_authenticated(username, password):
        ctx_ = dash.callback_context
        if not ctx_.triggered:
            return False, dash.no_update, False, None

        button_id = ctx_.triggered[0]['prop_id'].split('.')[0]

        if button_id == "delete-button":
            return True, dash.no_update, False, None
        elif button_id == "delete-confirmed":
            client = bigquery.Client()
            query = f"""
            DELETE FROM `dashapp-375513.data_science_job_hunt.applications` WHERE application_id = '{application_id}'
            """
            query_job = client.query(query)  # API request
            query_job.result() # Wait for the job to complete
            errors = query_job.errors
            if errors == [] or errors is None:
                return False, f"Application {application_id} deleted successfully.", False, 1
            else:
                return False, f"Encountered errors while deleting rows in Bigquery: {errors}", False, None
        return is_open, dash.no_update, False, None
    else:
        return False, "Authentication failed", True, None

# Callback to add core skills to the list in the dropdown
@app.callback(
    Output("core-skills-dropdown", "options"),
    Output("new-core-skill-input", "value"),
    Input("core-skills-dropdown", "options"),
    Input("new-core-skill-input", "n_submit"),
    State("new-core-skill-input", "value"),
    prevent_initial_call=True
)
def add_core_skill(skill_options, n_submit, new_skill):
    if n_submit is None or n_submit < 1:
        return dash.no_update
    elif new_skill is None:
        return dash.no_update
    print(skill_options)
    skill_options.append(new_skill)
    upload_options_to_gcs(skill_options, BUCKET_NAME, "core_skills_list.json")
    return skill_options, None

# Callback to add new Source to the list in the dropdown
@app.callback(
    Output("app-source-dropdown", "options"),
    Output("new-app-source-input", "value"),
    Input("app-source-dropdown", "options"),
    Input("new-app-source-input", "n_submit"),
    State("new-app-source-input", "value"),
    prevent_initial_call=True
)
def add_app_source(source_options, n_submit, new_source):
    if n_submit is None or n_submit < 1:
        return dash.no_update
    elif new_source is None:
        return dash.no_update
    source_options.append(new_source)
    upload_options_to_gcs(source_options, BUCKET_NAME, "application_source_list.json")
    return source_options, None