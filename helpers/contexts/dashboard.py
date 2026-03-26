import datetime
import hashlib
from functools import partial
from typing import Callable

from kombu import Message

from helpers.dataclasses.dashboard import MessageContext
from producers.dashboard import DashboardProducer


def create_message_context(message: Message, message_type: str, error_message: str = "",
                           obj_identifiers: dict | None = None) -> MessageContext:
    obj_identifiers = obj_identifiers or {}
    hash_str: str = hashlib.blake2b(str(message.payload).encode(), digest_size=8).hexdigest()
    message_type: str = message_type
    payload: str = message.payload or str(message.body)
    errored: bool = True if error_message else False
    error_message: str = error_message or ""
    return MessageContext(
        object_identifiers=obj_identifiers,
        processing_start=message.headers.get("received_at", datetime.datetime.now().isoformat()),
        processing_end=datetime.datetime.now().isoformat(),
        hash=hash_str,
        message_type=message_type,
        payload=payload,
        errored=errored,
        error_message=error_message,
        exchange_name=message.delivery_info["exchange"],
        routing_key=message.delivery_info["routing_key"],
    )


def get_configured_dashboard_callback(consumer: "PACERConsumer") -> Callable | None:
    dashboard_integration: dict = consumer.pacer_config.get("integrations", {}).get("dashboard", {})
    if dashboard_integration.get("enabled", False):
        exchange_name: str = dashboard_integration.get("exchangeName", "")
        routing_key: str = dashboard_integration.get("routingKey", "")
        celery_task: str = dashboard_integration.get("celeryTask", "")

        if exchange_name and routing_key and celery_task:
            func = partial(DashboardProducer.log_message, consumer.connection, exchange_name, routing_key, celery_task)
            return func
    return None
