import logging

import pytest
from psycopg_pool import ConnectionPool

from helpers.user import create_user_context, UserContext
from tasks.users import UserTasks
from tests.utils.generic_unit_test import GenericPACERUnitTest

logger: logging.Logger = logging.getLogger(__name__)


class TestVISAUserTasks(GenericPACERUnitTest):
    fixtures: list = ["user.json"]
    entities_teardown: list = ["User"]

    @pytest.fixture(scope="class")
    def user_tasks(self) -> UserTasks:
        return UserTasks(logger)

    @pytest.fixture(scope="class")
    def new_visa_user(self, unittest_user_prefix: str) -> UserContext:
        user_ctx: UserContext = create_user_context(self.fixtures_dict.get("user"),
                                                    username_prefix=unittest_user_prefix)
        return user_ctx

    def test_sync_visa_user(self, user_tasks: UserTasks, mock_psycopg_pool: ConnectionPool, new_visa_user: UserContext) -> None:
        user_tasks.sync_user_visa(mock_psycopg_pool, new_visa_user)

        calls: list = mock_psycopg_pool.connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value.execute.call_args_list
        sql_statements: list = [call.args[0] for call in calls]

        has_insert = any("INSERT" in sql.upper() for sql in sql_statements)
        assert has_insert, "No INSERT statements executed"
