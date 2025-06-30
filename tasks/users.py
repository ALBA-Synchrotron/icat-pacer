from __future__ import absolute_import, unicode_literals

import logging

from helpers.icat_utils import ICATClient
from helpers.user import UserContext


class UserTasks:

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger

    def sync_user_visa(self, user_context: UserContext, *_args, **_kwargs):
        self.logger.info(f"VISA sync: Synchronizing user {",".join(user_context.usernames)} visa")

    def sync_user_icat(self, icat_client: ICATClient, user_context: UserContext, *_args, **_kwargs):
        self.logger.info(f"ICAT sync: Synchronizing user {",".join(user_context.usernames)} visa")

        users: list = icat_client.search("User", conditions={"name__in": user_context.usernames}, flatten_single=False)
        if not users:
            users = [icat_client.new("User", name=i) for i in user_context.usernames]

        for u in users:
            u.fullName = f"{user_context.first_name} {user_context.last_name}"
            u.givenName = user_context.first_name
            u.familyName = user_context.last_name
            u.email = user_context.email
            u.orcidId = user_context.orcid
            u.affiliation = f"{", ".join(i for i in [user_context.affiliation.name, user_context.affiliation.unit, user_context.affiliation.department_name] if i != "")}"[
                            :255]
            u.name = u.name if user_context.enabled else f"{u.name}__user_disabled"

            if u.id:
                self.logger.info(f"ICAT sync: Updating user {u.name}")
                u.update()
            else:
                self.logger.info(f"ICAT sync: Creating user {u.name}")
                u.create()
