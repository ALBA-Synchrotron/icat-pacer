import pytest

from exceptions.dataset import DatasetNotFound, DatasetValidationError
from helpers.contexts.dataset import create_dataset_context
from helpers.static_settings import INPUT_DATASET_IDS_PARAMETER_NAME, INPUT_DATASET_PARAMETER_NAME, \
    OUTPUT_DATASET_IDS_PARAMETER_NAME, OUTPUT_DATASET_NAMES_PARAMETER_NAME
from helpers.utils.dataset import get_dataset_parameter


@pytest.fixture
def dataset_msg(request):
    return request.getfixturevalue(request.param)


class TestInternalDatasetConsumerDatasetLinkage:

    def test_asd(self):
        assert True == False
