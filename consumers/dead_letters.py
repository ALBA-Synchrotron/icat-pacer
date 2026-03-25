from __future__ import absolute_import, unicode_literals

import datetime
from typing import override

from kombu import Message

from exceptions.base import TooEarlyForRetry
from helpers.utils.pacer_consumer import PACERConsumer
from producers.generic import GenericProducer


class DeadLettersConsumer(PACERConsumer):

    # BEFORE ADDING (COPYING AND PASTING THIS CONSUMER TO CREATE A NEW ONE), REPLACE THE `dashboard_message_type`
    # SPECIFIED IN THE CALL TO THE SUPERIOR CLASS CONSTRUCTOR WITH A NEW VALUE FOR THE NEW MESSAGES TYPE.

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(dashboard_message_type="dead-letters", *args, **kwargs)

    @override
    def get_consumers(self, Consumer, channel) -> list:
        try:
            consumers: list = [
                Consumer(
                    queues=self.queues,
                    callbacks=[self.callback_func_dead_letter_retry],
                    accept=["text/plain", "application/json", "application/xml", ],
                    prefetch_count=1
                )
            ]
            return consumers
        except Exception as e:
            self.logger.error(f"Error setting up consumers: {e!r}")
            raise e

    def callback_func_dead_letter_retry(self, body, message: Message, *_args, **_kwargs) -> None:
        delay_seconds: int = message.headers.get("x-delay", 60)
        routing_key: str = message.headers.get("original-routing-key", "dead-letters")
        exchange: str = message.headers.get("original-exchange", "dead-letters")
        processing_ts: str = message.headers.get("x-processing-ts", datetime.datetime.now().isoformat())

        if datetime.datetime.fromisoformat(processing_ts) + datetime.timedelta(
                seconds=delay_seconds) < datetime.datetime.now():
            GenericProducer.send_message(self.connection, exchange_name=exchange,
                                         routing_key=routing_key,
                                         headers={**message.headers}, ctx=body)
            message.ack()
        else:
            message.reject(requeue=True)
