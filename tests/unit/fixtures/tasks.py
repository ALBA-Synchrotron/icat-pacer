import pytest

from tasks.datasets import DatasetsTasks
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


@pytest.fixture(scope="module")
def dataset_tasks(test_logger):
    return DatasetsTasks(test_logger)
