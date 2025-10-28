import datetime
from dataclasses import dataclass, field


@dataclass
class Affiliation:
    id: int = 0
    name: str = ""
    code: str = ""
    department_name: str = ""
    department_code: str = ""
    unit: str = ""
    city: str = ""
    country_code: str = ""


@dataclass
class UserContext:
    first_name: str
    last_name: str
    orcid: str = ""
    email: str = None
    is_staff: bool = False
    enabled: bool = False
    uos_id: int = None
    usernames: list[str] = None
    affiliation: Affiliation = field(default_factory=Affiliation)


@dataclass
class MessageContext:
    object_identifiers: dict
    processed_at: str = ""
    hash: str = ""
    message_type: str = ""
    payload_format: str = ""
    payload: str = ""
    errored: bool = False
    error_message: str = ""


@dataclass
class DashboardCeleryTask:
    id: str
    task: str
    args: list
    kwargs: dict
    retries: int = 10


@dataclass
class InvestigationOperationsContext:
    name: str
    operations: list


@dataclass
class InvestigationContext:
    name: str = ""
    facility: str = "ALBA"
    start_date: datetime = ""
    end_date: datetime = ""
    release_date: datetime = ""
    title: str = ""
    summary: str = ""
    instrument: dict = field(default_factory=lambda: {"name": "", "code": ""})
    type: str = ""
    user_list: list = field(default_factory=lambda: [{"username": "", "email": "", "role": ""}])
    visit_count: int = 0
    is_reimbursed: bool = False
    doi: str = ""
    url: str = ""
    visa_sync: bool = False
    icat_sync: bool = False


@dataclass
class DatasetSampleContext:
    name: str
    type: str


@dataclass
class DatasetDatafileContext:
    location: str
    size: str


@dataclass
class DatasetContext:
    investigation: str
    instrument: str
    name: str
    parameters: list
    location: str
    start_date: str
    end_date: str
    sample: DatasetSampleContext
    datafiles: list[DatasetDatafileContext]
