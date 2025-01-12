"""
This module contains utility functions that are used across the app.
"""

import json
import datetime
import pytz
from google.cloud import secretmanager, storage, bigquery
from google.cloud.exceptions import NotFound
from data.datamodel import Application

# Get the Chicago timezone
chicago_tz = pytz.timezone('America/Chicago')

# ---------------------------------------------------------------------
# Define BigQuery Schema
# ---------------------------------------------------------------------

with open("data/application_data_schema.json", encoding='utf-8') as json_file:
    data = json.load(json_file)

skills_field = [
            bigquery.SchemaField(
                "list", "STRUCT", 'REPEATED',
                fields=[
                    bigquery.SchemaField(
                        "element", "STRING"
                    )
                ]
            )
        ]

BQ_APP_SCHEMA = [
    bigquery.SchemaField(
        name=i['name'],
        field_type=i['type'],
        fields=skills_field if i['name']=='core_skills' else (),
        mode=i['mode'],
        default_value_expression=i['defaultValueExpression'] if 'defaultValueExpression' in i else None,
        description=i['description']
        ) for i in data
]

# ---------------------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------------------

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


def check_if_bigQuery_table_exists(client, table_ref):
    try:
        client.get_table(table_ref)
        return True
    except NotFound:
        return False


def upsert_data_to_bigQuery_table(
        application_upsert: Application,
        app_schema: list = BQ_APP_SCHEMA
        ):
    """
    BigQuery upsert operation to insert or update data in the applications table

    Args:
    ---
    application_upsert: Application - instance of the Application class
    app_schema: list - list of bigquery.SchemaField objects

    Returns:
    ---
    None
    """
    mainTableId = "dashapp-375513.data_science_job_hunt.applications"
    stagingTableId = "dashapp-375513.data_science_job_hunt.applications_staging"

    client = bigquery.Client()

    #Create main cron table if not present
    tablePresent = check_if_bigQuery_table_exists(client, mainTableId)
    if not tablePresent:
        table = bigquery.Table(mainTableId, schema=app_schema)
        table = client.create_table(table)  # Make an API request.
        print("Created main table {}.{}.{}".format(table.project, table.dataset_id, table.table_id))

    # Define the temporary staging table
    #Check is staging table is present
    stagingTablePresent = check_if_bigQuery_table_exists(client, stagingTableId)
    if stagingTablePresent:
        client.delete_table(stagingTableId, not_found_ok=True)
        print("Deleting staging table, id: {}".format(stagingTableId))

    job_config = bigquery.LoadJobConfig(schema=app_schema,
                                        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE)
    
    application_dict = application_upsert.model_dump()

    application_dict['application_date'] = '2024-01-01'
    application_dict['core_skills']  = {'list':[{'element':i} for i in application_dict['core_skills']]}

    # add timezones for Chicago
    application_dict['created_at'] = str(datetime.datetime.now().astimezone(pytz.timezone('America/Chicago')))
    application_dict['updated_at'] = str(datetime.datetime.now().astimezone(pytz.timezone('America/Chicago')))

    job = client.load_table_from_json([application_dict], stagingTableId, job_config=job_config)
    job.result()

    # Extract field names and values
    field_names = list(application_dict.keys())
    
    # Construct the UPDATE SET part
    update_set = ", ".join(
        [f"M.{field} = S.{field}" for field in field_names if field not in ("application_id", "created_at")]
        )
    
    # Construct the INSERT part
    insert_fields = ", ".join(field_names)
    insert_values = ", ".join([f"S.{field}" for field in field_names])

    # Construct the merge query
    merge_query = f"""
            MERGE INTO `dashapp-375513.data_science_job_hunt.applications` M
            USING `dashapp-375513.data_science_job_hunt.applications_staging` S
            ON M.application_id = S.application_id
            WHEN MATCHED THEN
            UPDATE SET
                {update_set}
            WHEN NOT MATCHED THEN
            INSERT ({insert_fields}) VALUES ({insert_values})
            """
    try:
        query_job = client.query(merge_query)
        query_job.result()  # Wait for the query to finish
        print("Merge operation completed successfully.")

        table = client.get_table(mainTableId)
        print("Loaded {} rows and {} columns to {}".format(table.num_rows, len(table.schema), mainTableId))

        client.delete_table(stagingTableId, not_found_ok=True)
        print("Deleting staging table, id: {}".format(stagingTableId))
        return query_job
    except Exception as err:
        print("Failed to merge data: {}".format(err))