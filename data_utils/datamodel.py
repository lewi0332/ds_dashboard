from typing import List, Optional, Any
from typing_extensions import Annotated
from datetime import date
from pydantic import BaseModel, BeforeValidator, Field
from dash_pydantic_form import fields, FormSection, AccordionFormLayout
from apps.utils import read_options_from_gcs, access_secrets

def ensure_id(value: Any)-> str:
    if isinstance(value, int):
        return str(value)
    else:
        return value

BUCKET_NAME = access_secrets("dashapp-375513", "BUCKET_NAME", "latest")

core_skills_list = read_options_from_gcs(BUCKET_NAME, "core_skills_list.json")
app_source_list = read_options_from_gcs(BUCKET_NAME, "application_source_list.json")

  
fields.Select.register_data_getter(
    lambda: [{"label": i, "value": i} for i in core_skills_list],
    "core_skills",
)
fields.Select.register_data_getter(
    lambda: [{"label": i, "value": i} for i in app_source_list],
    "application_source_list",
)

class Application(BaseModel):
    application_id: Annotated[str, BeforeValidator(ensure_id)] = Field(read_only=True, title="Application ID")
    application_date: date = date.today()
    application_link: Optional[str] = None
    company_name: str
    job_title: str
    location: Optional[str] = None
    office_participation: Optional[str] = None
    role_desc: Optional[str] = Field(
        title="Role Description",
        description="Summary of the role",
        default=None,
        json_schema_extra={"repr_type": "Textarea", "repr_kwargs":{"n_cols": 1.0}},
    )
    responsibilities: Optional[str] = Field(
        title="Respontibilities",
        description="Responsibilities of the role",
        default=None,
        json_schema_extra={"repr_type": "Textarea", "repr_kwargs":{"n_cols": 1.0}},
    )
    requirements: Optional[str] = Field(
        title="Requirements",
        description="Requirements of the role",
        default=None,
        json_schema_extra={"repr_type": "Textarea", "repr_kwargs":{"n_cols": 1.0}},
    )
    pay_min: int = Field(
        title="Pay - Lower Bound",
        description="Minimum pay for the role",
        default=0,
        json_schema_extra={"repr_type": "Number", "repr_kwargs": {"n_cols": .5}},
    )
    pay_max: int = Field(
        title="Pay - Upper Bound",
        description="Maximum pay for the role",
        default=0,
        json_schema_extra={"repr_type": "Number", "repr_kwargs": {"n_cols": .5}},
    )
    cv_version: Optional[str] = None
    cover_letter: Optional[str] = None
    self_assessment: int = Field(
        title="Self Assessment",
        description="Self assessment of the role",
        default=50,
        json_schema_extra={"repr_type": "Slider", "repr_kwargs": {"min": 0, "max": 100, "step": 1, "n_cols": 1.0}},
    )
    core_skills: List[str] = Field(
        default=['python', 'sql'],
        title="Core Skills",
        json_schema_extra={
            "repr_type": "ChipGroup",
            "repr_kwargs": {"multiple": True, "orientation": "horizontal", "data_getter": "core_skills", "n_cols": 1.0},
        },
    )
    llm: bool = Field(repr_type="Switch", default=False)
    mmm: bool = Field(repr_type="Switch", default=False)
    marketing: bool = Field(repr_type="Switch", default=False)
    retail: bool = Field(repr_type="Switch", default=False)
    healthcare: bool = Field(repr_type="Switch", default=False)
    finance: bool = Field(repr_type="Switch", default=False)
    senior_role: bool = Field(repr_type="Switch", default=False)
    staff_role: bool = Field(repr_type="Switch", default=False)
    generalist_role: bool = Field(repr_type="Switch", default=False)
    management_role: bool = Field(repr_type="Switch", default=False)
    refferal: bool = Field(repr_type="Switch", default=False)
    recruiter: bool = Field(repr_type="Switch", default=False)
    application_source: Optional[str] = Field(
        default="LinkedIn",
        title="Application Source",
        json_schema_extra={
            "repr_type": "Select",
            "repr_kwargs": {"data_getter": "application_source_list"},
        },
    )
    recruiter_screen: bool = False
    recruiter_screen_date: Optional[date] = None
    hiring_manager_screen: bool = False
    hiring_manager_screen_date: Optional[date] = None
    technical_screen: bool = False
    technical_screen_date: Optional[date] = None
    technical_screen_type: Optional[str] = None
    technical_screen_time: Optional[int] = 0
    offer: bool = False
    offer_date: Optional[date] = None
    rejection: bool = False
    rejection_date: Optional[date] = None


form_fields = AccordionFormLayout(
                sections=[
                    FormSection(
                        name="Application",
                        fields=[
                            "application_id",
                            "application_date",
                            "application_link",
                            "company_name",
                            "job_title",
                            "location",
                            "refferal",
                            "recruiter",
                            "application_source",
                            "office_participation",
                            "cv_version",
                            "cover_letter"
                            ],
                        default_open=True
                    ),
                    FormSection(
                        name="Description",
                        fields=[
                            "role_desc",
                            "responsibilities",
                            "requirements"
                        ],
                        default_open=True,
                    ),
                    FormSection(
                        name="Skills",
                        fields=["self_assessment",
                            "core_skills",
                            "llm",
                            "mmm",
                            "marketing",
                            "retail",
                            "healthcare",
                            "finance",
                            "senior_role",
                            "staff_role",
                            "generalist_role",
                            "management_role",
                        ],
                        default_open=True,
                    ),
                    FormSection(
                        name="Pay",
                        fields=["pay_min", "pay_max"],
                        default_open=True,
                    ),
                    FormSection(
                        name="Response",
                        fields=[
                            "recruiter_screen",
                            "recruiter_screen_date",
                            "hiring_manager_screen",
                            "hiring_manager_screen_date",
                            "technical_screen",
                            "technical_screen_date",
                            "technical_screen_type",
                            "technical_screen_time",
                            "offer",
                            "offer_date",
                            "rejection",
                            "rejection_date",
                            ],
                        default_open=True,
                    ),
                ],
            )

# Data mapping for the application form fields
application_form_fields = [
    ("application-id", "value", "application_id"),
    ("application-date", "date", "application_date"),
    ("application-link", "value", "application_link"),
    ("company-input", "value", "company_name"),
    ("job-title-input", "value", "job_title"),
    ("location-input", "value", "location"),
    ("office-participation-dropdown", "value", "office_participation"),
    ("role-desc-input", "value", "role_desc"),
    ("responsibilities-input", "value", "responsibilities"),
    ("requirements-input", "value", "requirements"),
    ("pay-min-input", "value", "pay_min"),
    ("pay-max-input", "value", "pay_max"),
    ("cv-version-input", "value", "cv_version"),
    ("cover-letter-input", "value", "cover_letter"),
    ("self-assessment-slider", "value", "self_assessment"),
    ("core-skills-dropdown", "value", "core_skills"),
    ("llm-switch", "on", "llm"),
    ("mmm-switch", "on", "mmm"),
    ("marketing-switch", "on", "marketing"),
    ("retail-switch", "on", "retail"),
    ("healthcare-switch", "on", "healthcare"),
    ("finance-switch", "on", "finance"),
    ("senior-role-switch", "on", "senior_role"),
    ("staff-role-switch", "on", "staff_role"),
    ("generalist-switch", "on", "generalist_role"),
    ("management-switch", "on", "management_role"),
    ("refferal-switch", "on", "refferal"),
    ("recruiter-switch", "on", "recruiter"),
    ("app-source-dropdown", "value", "application_source"),
    ("recruiter-screen-switch", "on", "recruiter_screen"),
    ("recruiter-screen-date", "date", "recruiter_screen_date"),
    ("hiring-manager-screen-switch", "on", "hiring_manager_screen"),
    ("hiring-manager-screen-date", "date", "hiring_manager_screen_date"),
    ("technical-screen-switch", "on", "technical_screen"),
    ("technical-screen-date", "date", "technical_screen_date"),
    ("technical-screen-type", "value", "technical_screen_type"),
    ("technical-screen-time", "value", "technical_screen_time"),
    ("offer-switch", "on", "offer"),
    ("offer-date", "date", "offer_date"),
    ("rejection-switch", "on", "rejection"),
    ("rejection-date", "date", "rejection_date"),
]