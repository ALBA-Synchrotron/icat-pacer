from __future__ import absolute_import, unicode_literals

import json
from dataclasses import asdict

from kombu import Connection

from helpers.dataclasses import MessageContext, DashboardCeleryTask


class DashboardProducer:

    @classmethod
    def log_message(cls, conn: Connection, exchange_name: str, routing_key: str, celery_task: str,
                    message_ctx: MessageContext) -> None:
        dashboard_task_json: DashboardCeleryTask = DashboardCeleryTask(task=celery_task, args=[],
                                                                       kwargs=asdict(message_ctx))
        json_msg: str = json.dumps(asdict(dashboard_task_json))
        with conn.Producer() as producer:
            producer.publish(
                json_msg,
                exchange=exchange_name,
                routing_key=routing_key,
                content_type="application/json",
                content_encoding="utf-8",
            )
