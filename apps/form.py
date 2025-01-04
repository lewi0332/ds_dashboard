import os
import time
import json
from datetime import date
import pandas as pd
import dash_daq as daq
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, ctx
from google.cloud import bigquery, secretmanager
from main import app
# Google BigQuery client
# client = bigquery.Client()

from apps.utils import access_secret_version, upload_options_to_gcs, read_options_from_gcs

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
            dcc.Dropdown(
                # read_options_from_gcs(BUCKET_NAME, "application_source_list.json"),
                options= ['Indeed', 'Glassdoor', 'Monster', 'LinkedIn', 'BuiltIn', 'Company Website'],
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
                html.Div(id="output-message", className="mt-3")
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
    State("current-application-store", "data"),
    State("application-id", "value"),
    State("application-date", "date"),
    State("application-link", "value"),
    State("company-input", "value"),
    State("job-title-input", "value"),
    State("location-input", "value"),
    State("office-participation-dropdown", "value"),
    State("role-desc-input", "value"),
    State("responsibilities-input", "value"),
    State("requirements-input", "value"),
    State("pay-min-input", "value"),
    State("pay-max-input", "value"),
    State("cv-version-input", "value"),
    State("cover-letter-input", "value"),
    State("self-assessment-slider", "value"),
    State("core-skills-dropdown", "value"),
    State("llm-switch", "on"),
    State("mmm-switch", "on"),
    State("marketing-switch", "on"),
    State("retail-switch", "on"),
    State("healthcare-switch", "on"),
    State("finance-switch", "on"),
    State("senior-role-switch", "on"),
    State("staff-role-switch", "on"),
    State("generalist-switch", "on"),
    State("management-switch", "on"),
    State("refferal-switch", "on"),
    State("recruiter-switch", "on"),
    State("recruiter-screen-switch", "on"),
    State("recruiter-screen-date", "date"),
    State("hiring-manager-screen-switch", "on"),
    State("hiring-manager-screen-date", "date"),
    State("technical-screen-switch", "on"),
    State("technical-screen-date", "date"),
    State("technical-screen-type", "value"),
    State("technical-screen-time", "value"),
    State("offer-switch", "on"),
    State("offer-date", "date"),
    State("rejection-switch", "on"),
    State("rejection-date", "date"),
    State('username', 'value'),
    State('password', 'value'),
    State('modal', 'is_open'),
    prevent_initial_call=True
)
def update_bigquery(submit_n_clicks,
                    login_n_clicks,
                    close_n_clicks,
                    raw_data,
                    app_id,
                    application_date,
                    app_link,
                    company,
                    job_title,
                    location,
                    office_participation,
                    role_desc,
                    responsibilities,
                    requirements,
                    pay_min,
                    pay_max,
                    cv_version,
                    cover_letter,
                    self_assessment,
                    core_skills,
                    llm,
                    mmm,
                    marketing,
                    retail,
                    healthcare,
                    finance,
                    senior_role,
                    staff_role,
                    generalist_role,
                    management_role,
                    refferal,
                    recruiter,
                    recruiter_screen,
                    recruiter_screen_date,
                    hiring_manager_screen,
                    hiring_manager_screen_date,
                    technical_screen,
                    technical_screen_date,
                    technical_screen_type,
                    technical_screen_time,
                    offer,
                    offer_date,
                    rejection,
                    rejection_date,
                    username,
                    password,
                    is_open):
    button_id = dash.callback_context

    button_id = button_id.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'submit-button':
        if username and password and is_authenticated(username, password):
            dff = pd.DataFrame(raw_data)

            if not app_id \
            or not application_date\
            or not company \
            or not job_title:
                return "Missing required fields."

            # Define the BigQuery table
            # table_id = "your_project.your_dataset.your_table"

            if pay_min == '':
                pay_min = 0
            if pay_max == '':
                pay_max = 0

            rows_to_insert = [
                    {"application_id": app_id,
                    "application_date": application_date,
                    "application_link": app_link,
                    "company_name": company, 
                    "job_title": job_title,
                    "location": location,
                    "office_participation": office_participation,
                    "role_desc": role_desc,
                    "responsibilities": responsibilities,
                    "requirements": requirements,
                    "pay_min": pay_min,
                    "pay_max": pay_max,
                    "cv_version": cv_version,
                    "cover_letter": cover_letter,
                    "self_assessment": self_assessment,
                    "core_skills": core_skills,
                    "llm": llm,
                    "mmm": mmm,
                    "marketing": marketing,
                    "retail": retail,
                    "healthcare": healthcare,
                    "finance": finance,
                    "senior_role": senior_role,
                    "staff_role": staff_role,
                    "generalist_role": generalist_role,
                    "management_role": management_role,
                    "refferal": refferal,
                    "recruiter": recruiter,
                    "recruiter_screen": recruiter_screen,
                    "recruiter_screen_date": recruiter_screen_date,
                    "hiring_manager_screen": hiring_manager_screen,
                    "hiring_manager_screen_date": hiring_manager_screen_date,
                    "technical_screen": technical_screen,
                    "technical_screen_date": technical_screen_date,
                    "technical_screen_type": technical_screen_type,
                    "technical_screen_time": technical_screen_time,
                    "offer": offer,
                    "offer_date": offer_date,
                    "rejection": rejection,
                    "rejection_date": rejection_date
                }
            ]

            new_row = pd.DataFrame(rows_to_insert)

            if app_id in dff["application_id"].values:
                dff.drop(dff[dff["application_id"] == app_id].index, inplace=True)
                dff = pd.concat([dff, new_row], ignore_index=True)
            else:
                dff = pd.concat([dff, new_row], ignore_index=True)

            dff.to_parquet("gs://dashapp-375513.appspot.com/data.parquet", index=False)
            
            # TODO Insert the row into BigQuery
            errors = []
            if errors == []:
                return f"Application {app_id} submitted successfully.", False, 1
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
    
    dff = pd.read_parquet("gs://dashapp-375513.appspot.com/data.parquet")

    if dff.empty:
        return "No data available.", [], None, None
    dff[['application_id', 'company_name', 'job_title']] = dff[['application_id', 'company_name', 'job_title']].fillna('').astype(str)
    # Get the options for the dropdown
    options = [{"label": row['company_name'] +' - ' + row['job_title'], "value": row["application_id"]} for index, row in dff.iterrows()]
    return "Data loaded successfully.", options, options[0]["value"], dff.to_dict("records")


# Callback to load the selected application
@app.callback(
    Output("application-id", "value"),
    Output("application-date", "date"),
    Output("application-link", "value"),
    Output("company-input", "value"),
    Output("job-title-input", "value"),
    Output("location-input", "value"),
    Output("office-participation-dropdown", "value"),
    Output("role-desc-input", "value"),
    Output("responsibilities-input", "value"),
    Output("requirements-input", "value"),
    Output("pay-min-input", "value"),
    Output("pay-max-input", "value"),
    Output("cv-version-input", "value"),
    Output("cover-letter-input", "value"),
    Output("self-assessment-slider", "value"),
    Output("core-skills-dropdown", "value"),
    Output("llm-switch", "on"),
    Output("mmm-switch", "on"),
    Output("marketing-switch", "on"),
    Output("retail-switch", "on"),
    Output("healthcare-switch", "on"),
    Output("finance-switch", "on"),
    Output("senior-role-switch", "on"),
    Output("staff-role-switch", "on"),
    Output("generalist-switch", "on"),
    Output("management-switch", "on"),
    Output("refferal-switch", "on"),
    Output("recruiter-switch", "on"),
    Output("recruiter-screen-switch", "on"),
    Output("recruiter-screen-date", "date"),
    Output("hiring-manager-screen-switch", "on"),
    Output("hiring-manager-screen-date", "date"),
    Output("technical-screen-switch", "on"),
    Output("technical-screen-date", "date"),
    Output("offer-switch", "on"),
    Output("offer-date", "date"),
    Output("rejection-switch", "on"),
    Output("rejection-date", "date"),
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
        return str(new_id), date.today(), "", "", "", "", "Hybrid", "", "", "", "", "", "", "", 50, ['python', 'pandas', 'sql'], False, False, False, False, False, False, False, False, False, False, False, False, False, None, False, None, False, None, False, None, False, None
    elif triggered_id == 'load-application-button':
        dff = pd.DataFrame(raw_data)
        row = dff[dff["application_id"] == application_id].iloc[0]
        if row["refferal"] == None:
            row["refferal"] = False
        return (
            row["application_id"],
            row["application_date"],
            row["application_link"],
            row["company_name"],
            row["job_title"],
            row["location"],
            row["office_participation"],
            row["role_desc"],
            row["responsibilities"],
            row["requirements"],
            row["pay_min"],
            row["pay_max"],
            row["cv_version"],
            row["cover_letter"],
            row["self_assessment"],
            row["core_skills"],
            row["llm"],
            row["mmm"],
            row["marketing"],
            row["retail"],
            row["healthcare"],
            row["finance"],
            row["senior_role"],
            row["staff_role"],
            row["generalist_role"],
            row["management_role"],
            row["refferal"],
            row["recruiter"],
            row["recruiter_screen"],
            row["recruiter_screen_date"],
            row["hiring_manager_screen"],
            row["hiring_manager_screen_date"],
            row["technical_screen"],
            row["technical_screen_date"],
            row["offer"],
            row["offer_date"],
            row["rejection"],
            row["rejection_date"]
        )


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
            dff = pd.DataFrame(raw_data)
            dff.drop(dff[dff["application_id"] == application_id].index, inplace=True)
            dff.to_parquet("gs://dashapp-375513.appspot.com/data.parquet", index=False)
            return False, f"Application {application_id} deleted successfully.", False, 1
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
    print(n_submit)
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
    print(n_submit)
    print(new_source)
    if n_submit is None or n_submit < 1:
        return dash.no_update
    elif new_source is None:
        return dash.no_update
    source_options.append(new_source)
    upload_options_to_gcs(source_options, BUCKET_NAME, "app_source_list.json")
    return source_options, None