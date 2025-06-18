from __future__ import absolute_import, unicode_literals

import logging

from helpers.pacer_consumer import PACERConsumer
from tasks.users import UserTasks


class UsersWorker(PACERConsumer):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.user_tasks = UserTasks()

    def callback_func_create_user_visa(self, body, message):
        self.logger.debug(f"Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        return self.user_tasks.sync_user_visa(body, message)

    def callback_func_create_user_icat(self, body, message):
        self.logger.info(f"Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        return self.user_tasks.sync_user_icat(body, message)
