import pytest
from data_utils.datamodel import Application, application_form_fields
from data_utils.upload_to_bq import BQ_APP_SCHEMA

def test_application_fields_in_bq_schema():
    """
    Ensure that all fields defined in the Application model are present in the BigQuery schema.
    Certain fields that are added during the upsert (e.g. timestamps) can be excluded.
    """
    # Get field names from the Application model
    model_field_names = set(Application.model_fields.keys())
    # Get field names from the BigQuery schema definition
    bq_field_names = set(field.name for field in BQ_APP_SCHEMA)
    
    # Exclude fields added during upload that might not be in the model
    allowed_extras = {"created_at", "updated_at"}
    missing_in_bq = model_field_names - bq_field_names - allowed_extras
    
    assert not missing_in_bq, f"The following Application fields are missing in the BQ schema: {missing_in_bq}"

def test_form_fields_match_model():
    """
    Ensure that all fields referenced in the form layout are present on the Application model.
    """
    # application_form_fields is a list of tuples. The 3rd element in each tuple is the model attribute.
    model_field_names = set(Application.model_fields.keys())
    form_model_fields = {mapping[2] for mapping in application_form_fields}
    
    missing_in_model = form_model_fields - model_field_names
    
    assert not missing_in_model, f"Form mapping references fields not in Application model: {missing_in_model}"