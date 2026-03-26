from dataclasses import dataclass


@dataclass
class MessageContext:
    object_identifiers: dict
    processing_start: str = ""
    processing_end: str = ""
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
