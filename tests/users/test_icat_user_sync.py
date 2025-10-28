import logging

import pytest

from helpers.integrations.icat_utils import ICATClient
from helpers.contexts.user import create_user_context, UserContext
from tasks.users import UserTasks
from tests.utils.generic_unit_test import GenericPACERUnitTest

logger: logging.Logger = logging.getLogger(__name__)


class TestICATUserTasks(GenericPACERUnitTest):
    fixtures: list = ["user.json"]
    entities_teardown: list = ["User"]

    @pytest.fixture(scope="class")
    def user_tasks(self) -> UserTasks:
        return UserTasks(logger)

    @pytest.fixture(scope="class")
    def new_icat_user(self, ascii_prefix) -> UserContext:
        user_ctx: UserContext = create_user_context(self.fixtures_dict.get("user"),
                                                    username_prefix=ascii_prefix)
        return user_ctx

    @pytest.fixture(scope="class")
    def updated_icat_user(self, new_icat_user: UserContext) -> UserContext:
        new_icat_user.first_name = "Updated"
        return new_icat_user

    @pytest.fixture(scope="class")
    def disabled_icat_user(self, new_icat_user: UserContext) -> UserContext:
        new_icat_user.enabled = False
        return new_icat_user

    def test_create_new_user(self, user_tasks: UserTasks, icat_client: ICATClient, new_icat_user: UserContext) -> None:
        user_tasks.sync_user_icat(icat_client, new_icat_user)
        users: list = icat_client.search("User", conditions={"name__in": new_icat_user.usernames}, flatten_single=False)

        assert len(users) == 2
        for count, i in enumerate(users):
            assert i.name == new_icat_user.usernames[count]

    def test_update_user(self, user_tasks: UserTasks, icat_client: ICATClient, updated_icat_user: UserContext) -> None:
        user_tasks.sync_user_icat(icat_client, updated_icat_user)
        users: list = icat_client.search("User", conditions={"name__in": updated_icat_user.usernames},
                                         flatten_single=False)

        assert len(users) == 2
        for i in users:
            assert i.givenName == updated_icat_user.first_name

    def test_disable_user(self, user_tasks: UserTasks, icat_client: ICATClient,
                          disabled_icat_user: UserContext) -> None:
        user_tasks.sync_user_icat(icat_client, disabled_icat_user)
        users: list = icat_client.search("User", conditions={"email__eq": disabled_icat_user.email},
                                         flatten_single=False)

        assert len(users) == 2
        for i in users:
            assert i.name.endswith("__user_disabled")
