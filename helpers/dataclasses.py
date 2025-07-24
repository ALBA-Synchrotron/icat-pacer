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
