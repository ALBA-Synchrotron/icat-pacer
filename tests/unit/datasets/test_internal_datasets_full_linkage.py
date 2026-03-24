import pytest

from exceptions.dataset import DatasetValidationError
from helpers.static_settings import FULL_INPUT_DATASET_IDS_PARAMETER_NAME, FULL_INPUT_DATASET_NAMES_PARAMETER_NAME


@pytest.fixture
def dataset_msg(request):
    return request.getfixturevalue(request.param)


class TestInternalDatasetLinksConsumer:

    def test_build_dataset_full_links_information_missing_dataset_id(self, icat_client, internal_dataset_links_tasks):
        with pytest.raises(DatasetValidationError):
            internal_dataset_links_tasks.build_dataset_full_links_information(icat_client, None)

    def test_build_dataset_full_links_information_non_existent_dataset(self, icat_client, internal_dataset_links_tasks):
        with pytest.raises(DatasetValidationError):
            internal_dataset_links_tasks.build_dataset_full_links_information(icat_client, 99999)

    def test_build_dataset_full_links_information(self, icat_client, internal_dataset_tasks,
                                                  internal_dataset_links_tasks,
                                                  generate_raw_proc_datasets,
                                                  create_raw_proc_datasets_relation):
        raw_datasets, proc_dataset = generate_raw_proc_datasets(4, 1)
        _, proc_dataset_2 = generate_raw_proc_datasets(0, 1)
        create_raw_proc_datasets_relation(raw_datasets, proc_dataset)
        create_raw_proc_datasets_relation(proc_dataset, proc_dataset_2)
        create_raw_proc_datasets_relation()

        internal_dataset_tasks.processed_dataset_linkage(icat_client, proc_dataset.id)
        internal_dataset_links_tasks.build_dataset_full_links_information(icat_client, proc_dataset.id)

        proc_dataset = icat_client.search("Dataset", conditions={"id__eq": proc_dataset.id}, flatten_single=True)
        proc_params = [(str(i.type.name), str(i.stringValue)) for i in proc_dataset.parameters]
        assert (FULL_INPUT_DATASET_IDS_PARAMETER_NAME, " ".join(str(i.id) for i in raw_datasets)) in proc_params
        assert (FULL_INPUT_DATASET_NAMES_PARAMETER_NAME, " ".join(i.name for i in raw_datasets)) in proc_params
