import json
import pytz
import datetime
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from data_utils.datamodel import Application

# Get the Chicago timezone
chicago_tz = pytz.timezone('America/Chicago')

# ---------------------------------------------------------------------
# Define BigQuery Schema
# ---------------------------------------------------------------------

with open("data_utils/application_data_schema.json", encoding='utf-8') as json_file:
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


    application_dict['core_skills']  = {'list':[{'element':i} for i in application_dict['core_skills']]}

    # convert date to string
    application_dict['application_date'] = str(application_dict['application_date'])

    # TODO: build this into pydantic model
    for i in ['recruiter_screen_date', 'hiring_manager_screen_date', 'technical_screen_date', 'offer_date', 'rejection_date']:
        if application_dict[i] is not None:
            application_dict[i] = str(application_dict[i])

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