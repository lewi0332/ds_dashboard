"""
This module contains utility functions that are used across the app.
"""

import json
from google.cloud import secretmanager, storage, bigquery
from google.cloud.exceptions import NotFound

# ---------------------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------------------

def access_secrets(project_id, secret_id, version_id, json_type=False):
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


def read_text_from_gcs(bucket_name: str, file_name: str) -> str:
    """
    Function to read the resume from Google Cloud Storage
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    text = blob.download_as_text()
    return text


def file_exists_in_gcs(bucket_name: str, blob_name: str)-> bool:
    """
    Check if a file exists in GCS
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.exists()


def read_json_from_gcs(bucket_name: str, file_name: str) -> dict:
    """
    Function to read the resume from Google Cloud Storage
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    text = json.loads(blob.download_as_text())
    return text


def upload_options_to_gcs(options: list, bucket_name: str, blob_name: str) -> bool:
    """
    Function to upload the options list to Google Cloud Storage

    Args:
    options: list - list of options used in dash dropdown to upload to gcs to be used in the app
    bucket_name: str - name of the bucket to upload to
    blob_name: str - name of the blob to upload to

    Returns:
    bool - True if successful
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(json.dumps(options), content_type='application/json')
    return True


def read_options_from_gcs(bucket_name: str, blob_name: str) -> list:
    """
    Function to read the options list from Google Cloud Storage into a Python list

    Args:
    bucket_name: str - name of the bucket to upload to
    blob_name: str - name of the blob to upload to

    Returns:
    list - list of options used in dash dropdown
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    options = json.loads(blob.download_as_text())
    return options
