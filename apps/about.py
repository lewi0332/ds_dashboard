import json
from io import BytesIO
from PIL import Image
from dash import html, dcc
import dash_bootstrap_components as dbc
from google.cloud import storage, secretmanager


def access_secret_version(project_id, secret_id, version_id, json_type=False):
    """
    Access the payload for the given secret version if one exists.
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")
    if json_type:
        payload = json.loads(payload)
    return payload

BUCKET_NAME = access_secret_version("dashapp-375513", "BUCKET_NAME", "latest")

storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)
blob = bucket.blob('NORDclose.jpg')
img = Image.open(BytesIO(blob.download_as_bytes()))

layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            [
                dcc.Markdown(id='intro',
                children = """
                ---
                # About Me
                ---
                """
                ),
                # center the image
                html.Img(src=img, style={'height':'7%',}, className='img-fluid'),
                html.Hr(),
                dcc.Markdown(
                """
                I’m searching for a **_“Data Science”_** role. But, even to those in the industry, that’s a wide description. Here’s the type of Data Scientist I am and what my ideal role looks like: 

                **I am more of a generalist than a specialist –**
                I love to tackle a little bit of ALL the data science issues around the business. Developing models to predict the things that matter. Setting up the statistical rigor around my own, or other’s, analysis or building the age old dashboard. And when I set up those predictive models or dashboards, I’ll gladly do some data engineering to build the data pipelines, orchestration, testing and monitoring in your preferred cloud service (AWS, Azure or GCP). However, if you need someone to whiteboard the math behind the latest attention model… I’m going to need a little time to brush up. 

                **Though, I do like to dive deep into a specific problem –**
                If it makes sense for the business to devote time to a big problem, I’m here to read the latest papers and test some new ideas. Recently I had the opportunity to design a Bayesian Sampling method to solve Marketing Mix Modeling. A fascinating and very challenging problem to crack.

                **I bring the experience of a long career in Marketing –**
                I spent nearly 20 years thinking about brand strategy, customer acquisition, public relations and retail operations. I led teams and helped build very well regarded retail brands. Since moving to data science, I have continued to work closely with marketing teams to drive digital marketing efficiency, find the right influencers, and measure the impact on the business. 

                **All that experience means I’m no spring chicken –**
                Age can be tricky in this field, but I see it as the ultimate strength and I champion my years of experience. I believe the data scientist should truly understand how the business works and have the confidence to say “no” when building the wrong product if it will not add value. I’ve been accountable to a P&L through two recessions and understand the strategy of the business as well as I understand the math behind the algorithms.

                **Aesthetics and storytelling are in my DNA –**
                Details matter. I have had a long obsession with good design and I try to bring that to reports, presentations, and most importantly, data visualizations. Telling the story is a foundational component to being a great data scientist. I consider the cognition of information in visuals, the storytelling arc to transmit a new idea, and I know that making things seem simple is very hard work.

                ---
                
                So, to bring all this to more digestible summary. 

                **As a data scientist, I would be a great fit...**

                - at a small or mid-size firm
                - where a generalist is needed
                - if you need to solve marketing/advertising data problems
                - if you need someone to also handle data engineering and MLops
                - if you're looking for someone self-guided and big picture aware
                - to lead a small team or the data strategy
                - if you're OK with someone a little too into bikes, Star Trek, and mechanical keyboards


                ---
                """,
                className='card-text',
                ),
            ]
        )
    ]),
])