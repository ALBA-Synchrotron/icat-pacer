import pytest

from tasks.users import UserTasks


@pytest.fixture(scope="module")
def user_tasks(test_logger):
    return UserTasks(test_logger)
