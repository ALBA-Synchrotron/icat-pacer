from __future__ import absolute_import, unicode_literals

import json
from dataclasses import asdict
from typing import TypeVar

from kombu import Connection

T = TypeVar("T")


class GenericProducer:

    @classmethod
    def send_message(cls, conn: Connection, exchange_name: str, routing_key: str, ctx: T, headers: dict = {}) -> None:

        try:
            json_msg: str = json.dumps(asdict(ctx))
            with conn.Producer() as producer:
                producer.publish(
                    json_msg,
                    exchange=exchange_name,
                    routing_key=routing_key,
                    content_type="application/json",
                    content_encoding="utf-8",
                    headers=headers
                )
        except Exception as e:
            error_msg: str = f"Error sending message to {exchange_name} with routing key {routing_key} through GenericProducer: {e}"
            raise Exception(error_msg)
