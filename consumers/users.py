from __future__ import absolute_import, unicode_literals

from kombu import Message

from helpers.dataclasses import UserContext
from helpers.pacer_consumer import PACERConsumer
from helpers.user import create_user_context
from tasks.users import UserTasks


class UsersConsumer(PACERConsumer):

    # BEFORE ADDING (COPYING AND PASTING THIS CONSUMER TO CREATE A NEW ONE), ENSURE THERE IS A MESSAGE TYPE SPECIFIED IN
    # THE `get_message_type` FUNCTION, INSIDE `helpers/dashboard.py` THAT MATCHES THE CLASS YOU WANT TO CREATE.
    # IF IT IS NOT SPECIFIED, MESSAGES WILL BE LOGGED WITH `unknown` TYPE.

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.tasks = UserTasks(self.logger)

    def callback_func_sync_user_visa(self, body, message: Message) -> None:
        self.logger.info(
            f"VISA_user_sync_callback > Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        user_str: str = message.payload or message.body
        user_context: UserContext = create_user_context(user_str)

        self.tasks.sync_user_visa(self.visa_pg_pool, user_context, message=message, body=body)

    def callback_func_sync_user_icat(self, body, message: Message) -> None:
        self.logger.info(
            f"ICAT_user_sync_callback > Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
        user_str: str = message.payload or message.body
        user_context: UserContext = create_user_context(user_str)

        self.tasks.sync_user_icat(self.icat_client, user_context, message=message, body=body)
