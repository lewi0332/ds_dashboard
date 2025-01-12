"""
# Temp Load existing parquet file to BigQuery

This script took the parquet file created early in the process and loaded
it into bigquery. The idea was that I wanted to start from the "create_schema.py"
step and force the data into BigQuery in order to test the schema.

This was a bit of a nightmare, but shows how I will need ot form the data
in the individual callbacks in the Dash app.
"""


import pandas as pd
from google.cloud import bigquery

dff = pd.read_parquet("gs://dashapp-375513.appspot.com/data.parquet")

date_cols= [
        'application_date',
        'recruiter_screen_date',
        'hiring_manager_screen_date',
        'technical_screen_date',
        'offer_date',
        'rejection_date']

for i in date_cols:
    dff[i] = pd.to_datetime(dff[i], format='%Y-%m-%d')

# add column 'created_at' with min date of all date columns in the `date_cols` list
# In the future this will happen in the Dash app
dff['created_at'] = pd.to_datetime(dff[date_cols].min(axis=1, skipna=True))
# add column 'updated_at' with max date of all date columns in the `date_cols` list
# In the future this will happen in the Dash app
dff['updated_at'] = pd.to_datetime(dff[date_cols].max(axis=1, skipna=True))

# Convert date columns to date type
for i in date_cols:
    dff[i] = pd.to_datetime(dff[i], format='%Y-%m-%d').dt.date

dff['application_source'] = 'N/A'

# This sucked. Just guessing for hours to get this to work
dff['core_skills'] = dff['core_skills'].apply(lambda x: {'list':[{'element':i} for i in x]})

client = bigquery.Client()

# Define your BigQuery table ID
table_id = 'dashapp-375513.data_science_job_hunt.applications'

schema = client.get_table(table_id).schema

errors = client.insert_rows_from_dataframe(dataframe=dff, table=table_id, selected_fields=schema)
errors
