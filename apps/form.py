import json
import time
from datetime import date
import pandas as pd
import dash_daq as daq
import dash
import dash_mantine_components as dmc
from dash import dcc, html, Input, Output, State, ctx, callback
from google.cloud import bigquery
from pydantic import ValidationError
from dash_pydantic_form import AccordionFormLayout, FormSection, ModelForm, fields, get_model_cls, ids
from data_utils.datamodel import Application, application_form_fields
from apps.utils import (
    access_secrets,
    upload_options_to_gcs)
from data_utils.upload_to_bq import upsert_data_to_bigQuery_table
from data_utils.datamodel import Application, form_fields
AIO_ID = "application-form"
FORM_ID = "Form"

# register_page(__name__, path="/form", name="Form", title="Form", description="Form to create and update job applications")

VALID_USERNAME_PASSWORD_PAIRS = access_secrets("dashapp-375513", "VALID_USERNAME_PASSWORD_PAIRS", "latest", json_type=True)

BUCKET_NAME = access_secrets(
    "dashapp-375513",
    "BUCKET_NAME",
    "latest")

# Layout of the app
form_layout = dmc.Container(
    children = [
        dcc.Markdown("""
                    ---
                    
                    # Job Application Form
                    ---
                    """,
                    className='card-text',
                    ),

        # Add button to load current data
        dmc.Select(
                id = "current-application-dropdown",
                label = "Select a Current Application to Edit",
                placeholder="Select an Application",
        ),
        html.Br(),
        dmc.Group(
            children = [
                dmc.Stack(
                    children = [
                        dmc.Button("Edit Application", id="load-application-button"),
                        html.Div(id="load-output-message", className="mt-3", style={'opacity': 0.5})
                    ],
                ),
            ],
            justify="flex-end",
        ),
        html.Hr(),
        dmc.Button("Reload Current Data", id="load-button", n_clicks=0,  style = dict(display='none')), 
        dmc.Group(
            children = [
                html.H3("Role Information"),
                dmc.Stack(
                    children = [
                        dmc.Button("Start New Application", id="new-button", n_clicks=0),
                        html.Div(id="new-output-message", className="mt-3", style={'opacity': 0.5}),
                    ],
                )
            ],
            justify="space-between",
        ),
        html.Div(id="main-form",
            children = [
                ModelForm(
                    item=Application,
                    aio_id=AIO_ID,
                    form_id=FORM_ID,
                    form_layout=form_fields
                ),
            ],
        ),
        dmc.Group(
            children = [
                dmc.Button("Submit", id="submit-button",),
                dmc.Button("Delete", id="delete-button",),
            ],
            justify="flex-end",

        ),
        dcc.Loading(id='loading_icon',
            children=[
                html.Div(id="output-message", className="mt-3")
            ],
            type='default'
        ),
        dmc.Space(h=40),
        dcc.Store(id="current-application-store", data=None),
        dmc.Modal(
            title="Login",
            children=[
                dmc.Stack([
                    dmc.Space(h=10),
                    dmc.TextInput(id='username', placeholder='Username', size='md'),
                    dmc.Space(h=10),
                    dmc.PasswordInput(id='password', placeholder='Password', size='md'),
                    dmc.Space(h=20),
                    dmc.Group([
                        dmc.Button("Login", id="login-button"),
                        dmc.Button(
                            "Close",
                            color="red",
                            variant="outline",
                            id="close",
                        ),
                    ],
                    justify="flex-end",
                    ),
                ])
            ],
            id="modal",
            opened=False,
        ),
        # Add an "are you sure" modal
        dmc.Modal(title = "Delete Application",
            children = [
                dmc.Text("Are you sure you want to delete this application?"),
                dmc.Space(h=20),
                dmc.Group(
                    [
                        dmc.Button("Delete", id="delete-confirmed"),
                        dmc.Button(
                            "Cancel",
                            color="red",
                            variant="outline",
                            id="delete-cancel",
                        ),
                    ],
                    justify="flex-end",
                ),
            ],
            id="delete-modal",
            opened=False
        ),
    ],
    fluid=True,
)




# Custom authentication check
def is_authenticated(username, password):
    return VALID_USERNAME_PASSWORD_PAIRS.get(username) == password

# Callback to handle form submission
@callback(
    Output("output-message", "children", allow_duplicate=True),
    Output('modal', 'opened'),
    Output("load-button", "n_clicks"),
    Input("submit-button", "n_clicks"),
    Input('login-button', 'n_clicks'),
    Input('close', 'n_clicks'),
    State('username', 'value'),
    State('password', 'value'),
    State('modal', 'opened'),
    State(ModelForm.ids.main(AIO_ID, FORM_ID), "data"),
    prevent_initial_call=True
)
def update_bigquery(submit_n_clicks,
                    login_n_clicks,
                    close_n_clicks,
                    username,
                    password,
                    is_open,
                    application_form_data):
    
    print(application_form_data)
    print(Application(**application_form_data))
    button_id = dash.callback_context
    button_id = button_id.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'submit-button':
        if username and password and is_authenticated(username, password):
            # Extract the values from the form and create an Application object
            # args = {application_form_fields[i][2]: args[i] for i in range(len(application_form_fields))}
            print(type(application_form_data))
            try:
                form_app = Application(**application_form_data)
            except ValidationError as pydantic_err:
                return pydantic_err, False, None
            
            job = upsert_data_to_bigQuery_table(form_app)
            job.result()
            errors = job.errors

            if errors == [] or errors is None:
                return f"Application {form_app.application_id} submitted successfully.", False, 1
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
@callback(
    Output("load-output-message", "children"),
    Output("current-application-dropdown", "data"),
    Output("current-application-store", "data"),
    Input("load-button", "n_clicks")
)
def load_data(n_clicks):
    """
    Load the data from BigQuery and return the options for the dropdown

    Store data in a hidden div to be used later
    """
    print(n_clicks)
    if n_clicks is None:
        return dash.no_update, dash.no_update, dash.no_update
    client = bigquery.Client()
    query = """
        SELECT
            application_id,
            company_name,
            job_title
        FROM `dashapp-375513.data_science_job_hunt.applications`
        ORDER BY company_name
    """
    dff = client.query_and_wait(query).to_dataframe()
    if dff.empty:
        return "No data available.", [], None
    dff[['application_id', 'company_name', 'job_title']] = dff[['application_id', 'company_name', 'job_title']].fillna('').astype(str)
    options = [{"label": row['company_name'] +' - ' + row['job_title'], "value": row["application_id"]} for index, row in dff.iterrows()]
    return "Data loaded successfully.", options, dff.to_dict("records")


# Callback to load the selected application
@callback(
    Output('main-form', "children"),
    Output("new-output-message", "children"),
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
        form = ModelForm(item=new_app, aio_id=AIO_ID, form_id=FORM_ID, form_layout=form_fields, store_progress="session")
        return form, 'New application created successfully.'
    
    elif triggered_id == 'load-application-button':
        # Load the record form bigquery where application_id = application_id store it as an Application object

        client = bigquery.Client()
        query = f"""
        SELECT * FROM `dashapp-375513.data_science_job_hunt.applications` WHERE application_id = '{application_id}'
        """
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
        form = ModelForm(item=Application(**row), aio_id=AIO_ID, form_id=FORM_ID, form_layout=form_fields, store_progress="session")
        return form, 'Application loaded successfully.'


# Add a delete button to delete the selected application with confirmation modal
@callback(
    Output("delete-modal", "opened"),
    Output("output-message", "children", allow_duplicate=True),
    Output('modal', 'opened', allow_duplicate=True),
    Output("load-button", "n_clicks", allow_duplicate=True),
    Input("delete-button", "n_clicks"),
    Input("delete-confirmed", "n_clicks"),
    State("delete-modal", "opened"),
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
@callback(
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
    skill_options.append(new_skill)
    upload_options_to_gcs(skill_options, BUCKET_NAME, "core_skills_list.json")
    return skill_options, None

# Callback to add new Source to the list in the dropdown
@callback(
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
