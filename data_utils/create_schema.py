import json

from google.cloud import bigquery
from apps.utils import file_exists_in_gcs, upload_options_to_gcs

# ---------------------------------------------------------------------
# Store base options in GCS
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

#TODO: Move this to a dynamic variable
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
# Create the BigQuery table
# ---------------------------------------------------------------------

client = bigquery.Client()
table_id = 'dashapp-375513.data_science_job_hunt.applications'
table = bigquery.Table(table_id, schema=BQ_APP_SCHEMA)
table = client.create_table(table)  # Make an API request.
print(
    "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
)

# ---------------------------------------------------------------------
# Store base options in GCS
# ---------------------------------------------------------------------

# Send options json to GCS
applicaton_sources_list = ['Indeed', 'Glassdoor', 'Monster', 'LinkedIn', 'BuiltIn', 'Company Website']

# Check if the options list is uploaded to GCS
if not file_exists_in_gcs('dashapp-375513.appspot.com', 'application_source_list.json'):
    upload_options_to_gcs(applicaton_sources_list, 'dashapp-375513.appspot.com', 'application_source_list.json')
    print('Uploaded application source list to GCS')
else:
    print('Application source list already exists in GCS')


# Send skill options json to GCS
core_skills_list = ['python',
                    'sql',
                    'numpy',
                    'pandas',
                    'scikit-learn',
                    'TensorFlow',
                    'matplotlib',
                    'seaborn',
                    'ggplot',
                    'tableau',
                    'powerbi',
                    'pytorch',
                    'keras',
                    'R',
                    'excel',
                    'spark',
                    'redshift',
                    'bigquery',
                    'snowflake',
                    'hypothesis_testing',
                    'inferential statistics',
                    'nlp',
                    'computer_vision',
                    'a_b_testing',
                    'regression_analysis',
                    'time_series_analysis',
                    'AWS',
                    'GCP',
                    'Azure',
                    'Docker',
                    'Kubernetes',
                    'CI/CD',
                    'Git',
                    'Agile',
                    'Scrum',
                    'Kanban',
                    'Jira',
                    'Confluence',
                    'GA4',
                    'customer_segmentation',
                    'customer_lifetime_value',
                    'churn_prediction',
                    'RFM',
                    'market_basket_analysis',
                    'airflow',
                    'Looker',
                    'DataDog',
                    'causal inference',
                    'experimentation',
                    'Optimization',
                    'GTM']
if not file_exists_in_gcs('dashapp-375513.appspot.com', 'core_skills_list.json'):
    upload_options_to_gcs(core_skills_list, 'dashapp-375513.appspot.com', 'core_skills_list.json')
    print('Uploaded skill options to GCS')
else:
    print('Skill options already exists in GCS')
