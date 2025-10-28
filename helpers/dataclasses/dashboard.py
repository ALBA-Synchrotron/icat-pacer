from dataclasses import dataclass


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
