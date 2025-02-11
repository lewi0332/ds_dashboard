import json
import pytz
import datetime
import logging
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from data_utils.datamodel import Application

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)

# Get the Chicago timezone
chicago_tz = pytz.timezone('America/Chicago')

# ---------------------------------------------------------------------
# Define BigQuery Schema
# ---------------------------------------------------------------------

with open("data_utils/application_data_schema.json", encoding='utf-8') as json_file:
    data = json.load(json_file)

# Define the schema for core_skills field
skills_field = [
    bigquery.SchemaField(
        "list", "STRUCT", 'REPEATED',
        fields=[
            bigquery.SchemaField("element", "STRING")
        ]
    )
]

BQ_APP_SCHEMA = [
    bigquery.SchemaField(
        name=i['name'],
        field_type=i['type'],
        fields=skills_field if i['name'] == 'core_skills' else (),
        mode=i['mode'],
        default_value_expression=i.get('defaultValueExpression', None),
        description=i['description']
    ) for i in data
]

def check_if_bigQuery_table_exists(client, table_ref):
    """
    Check if a BigQuery table exists.
    """
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

    # Create main table if not present
    tablePresent = check_if_bigQuery_table_exists(client, mainTableId)
    if not tablePresent:
        table = bigquery.Table(mainTableId, schema=app_schema)
        table = client.create_table(table)
        logging.info(f"Created main table {table.project}.{table.dataset_id}.{table.table_id}")
    else:
        logging.info(f"Main table {mainTableId} exists")

    # Check if staging table is present and delete if it exists
    stagingTablePresent = check_if_bigQuery_table_exists(client, stagingTableId)
    if stagingTablePresent:
        client.delete_table(stagingTableId, not_found_ok=True)
        logging.info(f"Deleting staging table, id: {stagingTableId}")
    else:
        logging.info(f"Staging table {stagingTableId} does not exist, proceeding")

    job_config = bigquery.LoadJobConfig(
        schema=app_schema,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )
    
    application_dict = application_upsert.model_dump()

    # Transform core_skills for BigQuery schema
    application_dict['core_skills'] = {'list': [{'element': i} for i in application_dict['core_skills']]}

    # Convert date to string
    application_dict['application_date'] = str(application_dict['application_date'])
    # Convert additional date fields if not None
    for field in ['recruiter_screen_date', 'hiring_manager_screen_date', 'technical_screen_date', 'offer_date', 'rejection_date']:
        if application_dict.get(field) is not None:
            application_dict[field] = str(application_dict[field])

    # Add timestamps (using Chicago timezone)
    now_chicago = str(datetime.datetime.now().astimezone(chicago_tz))
    application_dict['created_at'] = now_chicago
    application_dict['updated_at'] = now_chicago

    # Load data into the staging table
    job = client.load_table_from_json([application_dict], stagingTableId, job_config=job_config)
    job.result()
    logging.info(f"Loaded data into staging table: {stagingTableId}")

    # Build and execute the MERGE query
    field_names = list(application_dict.keys())
    update_set = ", ".join(
        [f"M.{field} = S.{field}" for field in field_names if field not in ("application_id", "created_at")]
    )
    insert_fields = ", ".join(field_names)
    insert_values = ", ".join([f"S.{field}" for field in field_names])

    merge_query = f"""
        MERGE INTO `{mainTableId}` M
        USING `{stagingTableId}` S
        ON M.application_id = S.application_id
        WHEN MATCHED THEN
        UPDATE SET {update_set}
        WHEN NOT MATCHED THEN
        INSERT ({insert_fields}) VALUES ({insert_values})
    """
    try:
        query_job = client.query(merge_query)
        query_job.result()  # Wait for the query to finish
        logging.info("Merge operation completed successfully.")
        
        table = client.get_table(mainTableId)
        logging.info(f"Loaded {table.num_rows} rows and {len(table.schema)} columns to {mainTableId}")
        
        client.delete_table(stagingTableId, not_found_ok=True)
        logging.info(f"Deleting staging table, id: {stagingTableId}")
        return query_job
    except Exception as err:
        logging.error(f"Failed to merge data: {err}")
        raise
