import datetime
import hashlib
import time
from functools import partial
from typing import Callable

from kombu import Message

from helpers.dataclasses import MessageContext
from producers.dashboard import DashboardProducer


def create_message_context(message: Message, message_type: str, error_message: str = "") -> MessageContext:
    processed_at: str = f"{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]} {time.strftime("%z")}"
    sha256_hash: str = hashlib.sha256(str(message.payload).encode()).hexdigest()
    message_type: str = message_type
    payload: str = message.payload or str(message.body)
    errored: bool = True if error_message else False
    error_message: str = error_message or ""
    return MessageContext(
        object_identifiers={},
        processed_at=processed_at,
        hash=sha256_hash,
        type=message_type,
        payload=payload,
        errored=errored,
        error_message=error_message,
    )


def get_configured_dashboard_callback(consumer: "PACERConsumer") -> Callable or None:
    dashboard_integration: dict = consumer.pacer_config.get("integrations", {}).get("dashboard", {})
    if dashboard_integration.get("enabled", False):
        exchange_name: str = dashboard_integration.get("exchangeName", "")
        routing_key: str = dashboard_integration.get("routingKey", "")
        celery_task: str = dashboard_integration.get("celeryTask", "")

        if exchange_name and routing_key and celery_task:
            func = partial(DashboardProducer.log_message, consumer.connection, exchange_name, routing_key, celery_task)
            return func
    return None
