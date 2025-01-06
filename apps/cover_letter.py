import json
import time
from google import genai
from google.genai import types
from google.cloud import secretmanager, storage
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback_context
from apps.utils import access_secret_version, read_text_from_gcs
from main import app


VALID_USERNAME_PASSWORD_PAIRS = access_secret_version(
    "dashapp-375513",
    "VALID_USERNAME_PASSWORD_PAIRS",
    "latest",
    json_type=True)

BUCKET_NAME = access_secret_version(
    "dashapp-375513",
    "BUCKET_NAME",
    "latest")

# Custom authentication check
def is_authenticated(username, password):
    return VALID_USERNAME_PASSWORD_PAIRS.get(username) == password

# Read in the resume from Google Cloud Storage
RESUME = read_text_from_gcs(BUCKET_NAME, "resume.txt")

def generate(
        job_description: str,
        company: str,
        platform: str = "LinkedIn",
        resume: str = RESUME, 
) -> str:
    client = genai.Client(
        vertexai=True,
        project="dashapp-375513",
        location="us-central1")

    cover_letter_prompt = types.Part.from_text(f"""You are a career counselor specializing in crafting compelling cover letters. Your task is to create a cover letter based on the provided resume and job description.  The cover letter should highlight the candidate\'s skills and experiences that align with the job requirements, showcasing their qualifications for the position. 

    **Instructions:**

    1. Carefully analyze the provided resume and job description.
    2. Identify key skills, experiences, and qualifications from the resume that match the requirements outlined in the job description.
    3. Structure the cover letter with a clear introduction, body paragraphs, and conclusion.
    4. In the introduction, express the candidate\'s interest in the specific position and company.
    5. In the body paragraphs, provide specific examples from the resume that demonstrate how the candidate\'s skills and experiences align with the job requirements. Quantify achievements whenever possible.
    6. In the conclusion, reiterate the candidate\'s enthusiasm and express their eagerness to learn more.
    7. Maintain a professional and positive tone throughout the cover letter.
    8. Adhere to standard cover letter formatting conventions and keep the body text to around 300 words or less.

    **Resume:**

    {resume}

    **Company Name:**

    {company}

    **Platform with the Job Posting:**

    {platform}

    **Job Description:**
    
    {job_description}

    **Generated Cover Letter:**""")

    model = "gemini-2.0-flash-exp"
    contents = [
        types.Content(
            role="user",
            parts=[
                cover_letter_prompt
            ]
        )
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=8192,
        response_modalities=["TEXT"],
        safety_settings=[types.SafetySetting(
            category="HARM_CATEGORY_HATE_SPEECH",
            threshold="OFF"
        ), types.SafetySetting(
            category="HARM_CATEGORY_DANGEROUS_CONTENT",
            threshold="OFF"
        ), types.SafetySetting(
            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
            threshold="OFF"
        ), types.SafetySetting(
            category="HARM_CATEGORY_HARASSMENT",
            threshold="OFF"
        )],
    )
    response_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        response_text += chunk.text  # Accumulate the text chunks

    return response_text

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2("Cover Letter Generator"),
            dbc.Input(id="company", placeholder="Company name"),
            html.Br(),
            dbc.Input(id="platform", placeholder="Platform with the job posting"),
            html.Br(),
            dbc.Textarea(id="job-description", placeholder="Enter job description here...", style={"height": "200px"}),
            dbc.Button("Generate Cover Letter", id="generate-button", color="primary", className="mt-3"),
            html.Div(id="cover-output-message", className="mt-3"),
            dcc.Loading(id='loading_icon',
                    children=[
                        dbc.Textarea(id="cover-letter", placeholder="Generated cover letter will appear here...", style={"height": "400px"}, readOnly=True, className="mt-3")
                    ],
                    type='default'
                ),
        ], width=12)
    ]),
    dbc.Modal(
        [
            dbc.ModalHeader("Login"),
            dbc.ModalBody([
                dbc.Input(id='username', placeholder='Username', type='text'),
                dbc.Input(id='password', placeholder='Password', type='password'),
                dbc.Button('Login', id='login-button', color='primary', className='mt-3')
            ]),
            dbc.ModalFooter(
                dbc.Button("Close", id="close", className="ml-auto")
            ),
        ],
        id="cover-modal",
        is_open=False,
    ),
])

# Combined callback to handle authentication, update graph, and toggle modal
@app.callback(
    Output('cover-letter', 'value'),
    Output('cover-output-message', 'children'),
    Output('cover-modal', 'is_open'),
    Input('generate-button', 'n_clicks'),
    Input('login-button', 'n_clicks'),
    Input('close', 'n_clicks'),
    State('company', 'value'),
    State('platform', 'value'),
    State('job-description', 'value'),
    State('username', 'value'),
    State('password', 'value'),
    State('cover-modal', 'is_open')
)
def update_graph_and_toggle_modal(
    submit_n_clicks,
    login_n_clicks,
    close_n_clicks,
    company,
    platform,
    job_description,
    username,
    password,
    is_open):
    ctx = callback_context

    if not ctx.triggered:
        return None, "", is_open

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'generate-button':
        if username and password and is_authenticated(username, password):
            return generate(company=company, platform= platform, job_description=job_description), "Authenticated", False
        else:
            return None, "Login to use Cover Letter Generator", True
    elif button_id == 'login-button':
        if is_authenticated(username, password):
            return generate(company=company, platform= platform, job_description=job_description), "Authenticated", False
        else:
            time.sleep(2)
            return None, "Authentication failed", True
    elif button_id == 'close':
        return None, "", False

    return None, "", is_open