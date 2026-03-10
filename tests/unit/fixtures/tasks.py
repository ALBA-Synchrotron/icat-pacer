import pytest

from tasks.investigation_ops import InvestigationOpsTasks
from tasks.investigations import ProposalTasks
from tasks.users import UserTasks


@pytest.fixture(scope="module")
def user_tasks(test_logger):
    return UserTasks(test_logger)


@pytest.fixture(scope="module")
def investigation_tasks(test_logger):
    return ProposalTasks(test_logger)

@pytest.fixture(scope="module")
def investigation_ops_tasks(test_logger):
    return InvestigationOpsTasks(test_logger)
