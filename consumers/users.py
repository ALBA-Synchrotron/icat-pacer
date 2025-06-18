from __future__ import absolute_import, unicode_literals

import logging
from typing import override

from kombu.mixins import ConsumerMixin

from conf.definitions import user_create_queue
from helpers.pacer_consumer import PACERConsumer
from tasks.users import UserTasks


class UsersWorker(PACERConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

        self.user_tasks = UserTasks()
    
    def callback_func_create_user_visa(self, body, message):
        self.logger.info(f"Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        return self.user_tasks.create_user_visa(body, message)

    def callback_func_create_user_icat(self, body, message):
        self.logger.info(f"Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        return self.user_tasks.create_user_icat(body, message)
