from __future__ import absolute_import, unicode_literals

import logging


class UserTasks:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_user_visa(self, body, message):
        """ Process of user creation."""
        try:
            self.logger.info("Starting create_user_visa task")
            user_dict = message.payload or message.body
            #
            # TODO: USER CREATION LOGIC GOES HERE
            #
            self.logger.info("Finished create_user_visa task")
        except Exception as e:
            self.logger.error(f"Error processing create_user_visa message: {e!r}")
            message.reject(requeue=True)  # when to requeue?
            return

    def create_user_icat(self, body, message):
        """ Process of user creation."""
        try:
            self.logger.info("Starting create_user_icat task")
            user_dict = message.payload or message.body
            #
            # TODO: USER CREATION LOGIC GOES HERE
            #
            message.ack()
            self.logger.info("Finished create_user_icat task")
        except Exception as e:
            self.logger.error(f"Error processing create_user_icat message: {e!r}")
            message.reject(requeue=True)  # when to requeue?
            return
