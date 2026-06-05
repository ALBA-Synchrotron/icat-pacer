import datetime
from typing import Union

from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, field_validator, model_validator

from helpers.utils.datetime import try_parse_datetime


class InvestigationOperationsContext(BaseModel):
    name: str
    operations: list
    visit_id: str


class InvestigationInstrumentContext(BaseModel):
    name: str
    code: str


class InvestigationUserContext(BaseModel):
    username: str
    email: str
    role: str


class InvestigationContext(BaseModel):
    name: str
    facility: str
    start_date: datetime.datetime
    end_date: datetime.datetime
    release_date: Union[datetime.datetime, None]
    title: str
    summary: str
    instrument: InvestigationInstrumentContext
    type: str
    user_list: list[InvestigationUserContext]
    icat_visit_id: str
    visa_visit_id: int
    sample_acronyms: list[str]
    is_industrial: bool
    visit_count: int = 0
    is_reimbursed: bool = False
    visa_sync: bool = False
    icat_sync: bool = False
    sample_acronyms: list[str] = []

    @field_validator("start_date", "end_date", "release_date", mode="before")
    @classmethod
    def validate_datetime(cls, value):
        if value is None:
            return None

        if isinstance(value, datetime):
            return value

        try:
            return try_parse_datetime(value)
        except Exception as exc:
            raise ValueError(f"Invalid datetime: {value}") from exc

    @model_validator(mode="after")
    def calculate_release_date(self):
        if not self.is_industrial:
            self.release_date = relativedelta(years=ingestion_settings.get("defaultEmbargoYears", 3))
        return self