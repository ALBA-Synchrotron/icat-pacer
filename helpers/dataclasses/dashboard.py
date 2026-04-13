from dataclasses import dataclass


@dataclass
class MessageContext:
    object_identifiers: dict
    error_message: dict
    processing_start: str = ""
    processing_end: str = ""
    hash: str = ""
    message_type: str = ""
    payload_format: str = ""
    payload: str = ""
    errored: bool = False
    exchange_name: str = ""
    routing_key: str = ""


@dataclass
class DashboardCeleryTask:
    id: str
    task: str
    args: list
    kwargs: dict
    retries: int = 10
