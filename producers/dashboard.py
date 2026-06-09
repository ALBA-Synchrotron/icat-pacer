from __future__ import absolute_import, unicode_literals

import json
import uuid

from kombu import Connection

from helpers.models.dashboard import MessageContext, DashboardCeleryTask


class DashboardProducer:

    @classmethod
    def log_message(cls, conn: Connection, exchange_name: str, routing_key: str, celery_task: str,
                    message_ctx: MessageContext) -> None:
        dashboard_task_json: DashboardCeleryTask = DashboardCeleryTask.model_validate(
            {
                "task": celery_task, "args": [],
                "kwargs": dict(message_ctx), "id": str(uuid.uuid4())}
        )
        json_msg: str = dashboard_task_json.model_dump_json()
        with conn.Producer() as producer:
            producer.publish(
                json_msg,
                exchange=exchange_name,
                routing_key=routing_key,
                content_type="application/json",
                content_encoding="utf-8",
            )
