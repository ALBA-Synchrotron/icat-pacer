import pytest

from tasks.datasets import DatasetsTasks
from tasks.datasets_indexing import DatasetsIndexingTasks
from tasks.datasets_internal import DatasetsInternalTasks
from tasks.internal_dataset_links import InternalDatasetLinksTasks
from tasks.internal_statistics import InternalStatisticsTasks
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

@pytest.fixture(scope="module")
def internal_dataset_tasks(test_logger):
    return DatasetsInternalTasks(test_logger)

@pytest.fixture(scope="module")
def internal_statistics_tasks(test_logger):
    return InternalStatisticsTasks(test_logger)

@pytest.fixture(scope="module")
def internal_dataset_links_tasks(test_logger):
    return InternalDatasetLinksTasks(test_logger)

@pytest.fixture(scope="module")
def datasets_indexing_tasks(test_logger):
    return DatasetsIndexingTasks(test_logger)