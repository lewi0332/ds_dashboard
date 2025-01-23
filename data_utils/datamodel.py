from typing import List, Optional, Any
from typing_extensions import Annotated
from datetime import datetime, date
from pydantic import BaseModel, BeforeValidator


def ensure_id(value: Any)-> str:
    if value is int:
        return str(value)
    else:
        return value

class Application(BaseModel):
    application_id: Annotated[str, BeforeValidator(ensure_id)]
    application_date: date = date.today()
    application_link: Optional[str] = None
    company_name: str
    job_title: str
    location: Optional[str] = None
    office_participation: Optional[str] = None
    role_desc: Optional[str] = None
    responsibilities: Optional[str] = None
    requirements: Optional[str] = None
    pay_min: int = 0
    pay_max: int = 0
    cv_version: Optional[str] = None
    cover_letter: Optional[str] = None
    self_assessment: int = 50
    core_skills: List[str] = ['python', 'sql']
    llm: bool = False
    mmm: bool = False
    marketing: bool = False
    retail: bool = False
    healthcare: bool = False
    finance: bool = False
    senior_role: bool = False
    staff_role: bool = False
    generalist_role: bool = False
    management_role: bool = False
    refferal: bool = False
    recruiter: bool = False
    application_source: Optional[str] = None
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