from __future__ import absolute_import, unicode_literals

import json
from dataclasses import asdict

from kombu import Connection

from helpers.dataclasses import MessageContext


class DashboardProducer:

    @classmethod
    def log_message(cls, conn: Connection, exchange_name: str, routing_key: str, message_ctx: MessageContext) -> None:
        json_msg: str = json.dumps(asdict(message_ctx))
        with conn.Producer() as producer:
            producer.publish(
                json_msg,
                exchange=exchange_name,
                routing_key=routing_key,
                content_type="application/json",
                content_encoding="utf-8",
            )
