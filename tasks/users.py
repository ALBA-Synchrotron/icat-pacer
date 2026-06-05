from __future__ import absolute_import, unicode_literals

import logging

from psycopg_pool import ConnectionPool

from helpers.integrations.icat.extended_client import ICATClient
from helpers.integrations.visa_utils import VISALoader
from helpers.models.user import UserContext
from helpers.utils.base_tasks import BaseTasks


class UserTasks(BaseTasks):
    USER_DISABLED_SUFFIX: str = "__user_disabled"

    def __init__(self, logger: logging.Logger = None):
        super().__init__(logger)

    def sync_user_visa(self, pg_pool: ConnectionPool, user_context: UserContext, *_args, **_kwargs) -> None:
        self.logger.info(f"VISA sync: Synchronizing user {','.join(user_context.usernames)}")

        VISALoader.db_sync_affiliation(pg_pool, user_context.affiliation, self.logger)
        VISALoader.db_sync_user(pg_pool, user_context, self.logger)

    def sync_user_icat(self, icat_client: ICATClient, user_context: UserContext, *_args, **_kwargs) -> None:
        self.logger.info(f"ICAT sync: Synchronizing user {','.join(user_context.usernames)}")

        user_usernames: list = [*user_context.usernames,
                                *[f"{i}{self.USER_DISABLED_SUFFIX}" for i in user_context.usernames]]

        users: list = icat_client.search("User", conditions={"name__in": user_usernames}, flatten_single=False)
        if not users:
            users = [icat_client.new("User", name=i) for i in user_context.usernames]

        for u in users:
            u.fullName = f"{user_context.first_name} {user_context.last_name}"
            u.givenName = user_context.first_name
            u.familyName = user_context.last_name
            u.email = user_context.email
            u.orcidId = user_context.orcid
            u.affiliation = user_context.affiliation.get_affiliation_name(limit=255)
            u.name = u.name.lower()
            u.name = u.name.replace(self.USER_DISABLED_SUFFIX,
                                    "") if user_context.enabled else \
                u.name if u.name.endswith(self.USER_DISABLED_SUFFIX) else \
                    f"{u.name}{self.USER_DISABLED_SUFFIX}"

            if u.id:
                self.logger.info(f"ICAT sync: Updating user {u.name}")
                u.update()
            else:
                self.logger.info(f"ICAT sync: Creating user {u.name}")
                u.create()
