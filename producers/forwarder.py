from __future__ import absolute_import, unicode_literals

from kombu import Message, Connection


class MessageForwarder:

    @classmethod
    def forward_message(cls, conn: Connection, message: Message) -> None:
        with conn.Producer() as producer:
            producer.publish(
                message.body,
                exchange=message.delivery_info['exchange'],
                routing_key=message.delivery_info['routing_key'],
                headers=message.headers,
            )
