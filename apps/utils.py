import json
from google.cloud import secretmanager, storage

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

# Function to read the resume from Google Cloud Storage
def read_text_from_gcs(bucket_name, file_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    text = blob.download_as_text()
    return text

# Function to read the resume from Google Cloud Storage
def read_json_from_gcs(bucket_name, file_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    text = json.loads(blob.download_as_text())
    return text

# Function to upload the options list to Google Cloud Storage
def upload_options_to_gcs(options, bucket_name, blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(json.dumps(options), content_type='application/json')
    return True

# Function to read the options list from Google Cloud Storage into a Python list
def read_options_from_gcs(bucket_name, blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    options = json.loads(blob.download_as_text())
    return options
