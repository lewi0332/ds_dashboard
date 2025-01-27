import json
from dash import html, dcc, register_page, callback
import plotly.io as pio
import dash_mantine_components as dmc
from google.cloud import storage, secretmanager

register_page(__name__)

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


blob_name = f'clusters_3d.json'
blob = bucket.blob(blob_name)
with blob.open('r') as outfile:
    cluster3d = pio.from_json(json.load(outfile))

# Dummy page to get started.
layout = dmc.Container(
    children=[
        dcc.Markdown(
            children = """
            ---
            # Segmentation
            ---

            ### Coming soon!

            This page will contain a tool to segment roles based on skills, requirements, and responsibilities.

            This may be an interesting tool for me to understand the market, though unlikely to be useful for job hunting.
            It will test my ability to compentently use NLP and clustering techniques.
            
            ---
            """,
            className='card-text',
        ),
        dcc.Graph(figure=cluster3d),
        html.Br(),
    ],
    fluid=True
)