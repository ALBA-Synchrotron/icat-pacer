from __future__ import absolute_import, unicode_literals

import logging
from typing import Any, Optional

from kombu import Producer, Exchange, Connection


class MessagePublisher:
    def __init__(self,
                 connection,
                 exchange: Exchange,
                 routing_key: str,
                 serializer: Optional[str] = "json",
                 content_type: str = 'application/json',
                 content_encoding: str = 'utf-8'
                 ) -> None:

        self.logger = logging.getLogger(__name__)

        self.content_type = content_type
        self.content_encoding = content_encoding

        if serializer is not None:
            self.logger.info(f"Using serializer: {serializer}")
            self.content_type = None

        self.producer = Producer(connection, exchange=exchange, routing_key=routing_key, serializer=serializer)

    def send_message(self, message: Any) -> None:

        """
        Generic method to send a message to the specified broker exchange.
        """
        self.producer.publish(
            message,
            content_type=self.content_type,
            content_encoding=self.content_encoding,
        )
        self.logger.info("Message sent.")
