from __future__ import absolute_import, unicode_literals

import logging

from helpers.icat_utils import ICATClient
from helpers.user import UserContext


class UserTasks:

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger

    def sync_user_visa(self, icat_client: ICATClient, user_context: UserContext, *_args, **_kwargs):
        self.logger.info(f"VISA sync: Synchronizing user {",".join(user_context.usernames)} visa")

    def sync_user_icat(self, icat_client: ICATClient, user_context: UserContext, *_args, **_kwargs):
        self.logger.info(f"ICAT sync: Synchronizing user {",".join(user_context.usernames)} visa")

        users = icat_client.search("User", conditions={"name__in": user_context.usernames}, flatten_single=False)
        asd = 23
