from __future__ import absolute_import, unicode_literals

from kombu import Message

from helpers.models.user import UserContext
from helpers.utils.pacer_consumer import PACERConsumer, callback_order
from helpers.contexts.user import create_user_context
from tasks.users import UserTasks


class UsersConsumer(PACERConsumer):

    # BEFORE ADDING (COPYING AND PASTING THIS CONSUMER TO CREATE A NEW ONE), REPLACE THE `dashboard_message_type`
    # SPECIFIED IN THE CALL TO THE SUPERIOR CLASS CONSTRUCTOR WITH A NEW VALUE FOR THE NEW MESSAGES TYPE.

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(dashboard_message_type="user-sync", *args, **kwargs)
        self.tasks = UserTasks(self.logger)

    def get_message_object_identifiers(self, message: Message, shared_obj_identifiers: dict = {}) -> dict:
        try:
            user_str: str = message.payload or message.body
            user_context: UserContext = create_user_context(user_str)
            return {"profile_id": user_context.uos_id, "usernames": user_context.usernames, **shared_obj_identifiers}
        except Exception as e:
            self.logger.error(f"Error getting message object identifiers: {e!r}")
            return {}

    @callback_order(1)
    def callback_func_sync_user_visa(self, body, message: Message, *_args, **_kwargs) -> None:
        if "visa" in self.integrations:
            self.logger.info(
                f"VISA_user_sync_callback > Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
            user_str: str = message.payload or message.body
            user_context: UserContext = create_user_context(user_str)

            self.tasks.sync_user_visa(self.visa_pg_pool, user_context, message=message, body=body)

    @callback_order(2)
    def callback_func_sync_user_icat(self, body, message: Message, *_args, **_kwargs) -> None:
        if "icat" in self.integrations:
            self.logger.info(
                f"ICAT_user_sync_callback > Processing message from {message.delivery_info['routing_key']}: {message.payload!r}")
            user_str: str = message.payload or message.body
            user_context: UserContext = create_user_context(user_str)

        self.tasks.sync_user_icat(self.icat_client, user_context, message=message, body=body)
