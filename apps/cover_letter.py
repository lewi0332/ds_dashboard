import json
import time
from google import genai
from google.genai import types
import dash_mantine_components as dmc
from dash import html, dcc, Input, Output, State, callback_context, register_page, callback
from apps.utils import access_secret_version, read_text_from_gcs

register_page(__name__)

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

layout = dmc.Container([
    # dmc.Group([
        html.H2("Cover Letter Generator"),
        dmc.TextInput(id="company", placeholder="Company name", label="Company Name", w="400", size="xl"),
        html.Br(),
        dmc.TextInput(id="platform", placeholder="Platform with the job posting", label="Platform", w="400", size="xl"),
        html.Br(),
        dmc.RadioGroup(
            id='resume-choice',
            children=[
                dmc.Radio('Use Default Resume', value='default', my=10),
                dmc.Radio('Add Custom Resume', value='custom', my=10)
            ],
            value='default',
            label= 'Resume Options',
            mb=10,
            mt=10,
            size="xl",
        ),
        html.Br(),
        dmc.Textarea(id="custom-resume", 
                     placeholder="Enter custom resume here...", 
                     value=None,
                     label='Custom Resume',
                     maxRows=300,
                     size="xl",
                     style={"height": "200px", "display": "none"},
                     w="75%"
        ),
        html.Br(),
        dmc.Textarea(id="job-description",
                     placeholder="Enter job description here...",
                     label='Job Description',
                     maxRows=300,
                     size="xl",
                     style={"height": "500px"},
                     w="75%"
        ),
        dmc.Button("Generate Cover Letter", id="generate-button",  className="mt-3"),
        html.Br(),
        html.Div(id="cover-output-message", className="mt-3"),
        dcc.Loading(id='loading_icon',
                children=[
                    dmc.Textarea(id="cover-letter",
                                 placeholder="Generated cover letter will appear here...",
                                 label='Cover Letter',
                                 style={"height": "400px"},
                                 readOnly=True,
                                 autosize=True,
                                 className="mt-3",
                                 w="75%",
                                 size="xl",
                    )
                ],
                type='default'
        ),
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
        id="cover-modal",
        opened=False,
    ),
],
fluid=True
)

# Combined callback to handle authentication, update graph, and toggle modal
@callback(
    Output('cover-letter', 'value'),
    Output('cover-output-message', 'children'),
    Output('cover-modal', 'opened'),
    Input('generate-button', 'n_clicks'),
    Input('login-button', 'n_clicks'),
    Input('close', 'n_clicks'),
    State('company', 'value'),
    State('platform', 'value'),
    State('custom-resume', 'value'),
    State('job-description', 'value'),
    State('username', 'value'),
    State('password', 'value'),
    State('cover-modal', 'opened')
)
def update_graph_and_toggle_modal(
    submit_n_clicks,
    login_n_clicks,
    close_n_clicks,
    company,
    platform,
    custom_resume,
    job_description,
    username,
    password,
    opened):
    ctx = callback_context

    if not ctx.triggered:
        return None, "", opened

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if custom_resume is None:
        custom_resume = RESUME

    if button_id == 'generate-button':
        if username and password and is_authenticated(username, password):
            return generate(company=company, platform= platform, job_description=job_description, resume=custom_resume), "Authenticated", False
        else:
            return None, "Login to use Cover Letter Generator", True
    elif button_id == 'login-button':
        if is_authenticated(username, password):
            return generate(company=company, platform= platform, job_description=job_description, resume=custom_resume), "Authenticated", False
        else:
            time.sleep(4)
            return None, "Authentication failed", True
    elif button_id == 'close':
        return None, "", False

    return None, "", opened

@callback(
    Output('custom-resume', 'style'),
    Input('resume-choice', 'value')
)
def toggle_custom_resume(resume_choice):
    if resume_choice == 'custom':
        return {"height": "200px", "display": "block"}
    else:
        return {"height": "200px", "display": "none"}
