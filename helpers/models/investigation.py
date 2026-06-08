import datetime
from typing import Union

from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, field_validator, model_validator, Field

from exceptions.investigation import InvestigationValidationError
from globals_var import ingestion_settings
from helpers.static_settings import ICAT_USER_ROLES
from helpers.utils.datetime import try_parse_datetime


class InvestigationInstrumentContext(BaseModel):
    name: str = Field(min_length=1)
    code: str = Field(min_length=1)


class InvestigationUserContext(BaseModel):
    username: str = Field(min_length=1)
    email: str = Field(min_length=1)
    role: str = Field(description=f"Allowed values: {', '.join(ICAT_USER_ROLES.values())}")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v not in ICAT_USER_ROLES.values():
            raise InvestigationValidationError(f"Invalid role: {v}")
        return v


class InvestigationContext(BaseModel):
    name: str = Field(min_length=1)
    facility: str = Field(min_length=1)
    start_date: Union[str, datetime.datetime]
    end_date: Union[str, datetime.datetime]
    release_date: Union[datetime.datetime, None] = None
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    instrument: InvestigationInstrumentContext
    type: str = Field(min_length=1)
    user_list: list[InvestigationUserContext]
    icat_visit_id: str = Field(min_length=1)
    visa_visit_id: int = Field(gt=0)
    sample_acronyms: list[str]
    is_industrial: bool
    visit_count: int = 0
    is_reimbursed: bool = False
    visa_sync: bool = False
    icat_sync: bool = False
    sample_acronyms: list[str] = []

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def validate_datetime(cls, value):
        if value is None:
            return None

        if isinstance(value, datetime.datetime):
            return value

        try:
            return try_parse_datetime(value)
        except Exception as exc:
            raise ValueError(f"Invalid datetime: {value}") from exc

    @model_validator(mode="after")
    def calculate_release_date(self):
        if not self.is_industrial:
            self.release_date = self.end_date + relativedelta(years=ingestion_settings.get("defaultEmbargoYears", 3))
        return self
