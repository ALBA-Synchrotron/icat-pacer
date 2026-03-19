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

    def test_link_missing_dataset_id_raw_dataset(self, internal_dataset_tasks, icat_client):
        with pytest.raises(DatasetValidationError):
            internal_dataset_tasks.raw_dataset_linkage(icat_client, 889981)

    def test_link_missing_dataset_id_proc_dataset(self, internal_dataset_tasks, icat_client):
        with pytest.raises(DatasetValidationError):
            internal_dataset_tasks.processed_dataset_linkage(icat_client, 889981)

    def test_link_non_existent_raw_dataset(self, internal_dataset_tasks, icat_client):
        with pytest.raises(DatasetNotFound):
            internal_dataset_tasks.raw_dataset_linkage(icat_client, 889981)

    def test_link_non_existent_proc_dataset(self, internal_dataset_tasks, icat_client):
        with pytest.raises(DatasetNotFound):
            internal_dataset_tasks.processed_dataset_linkage(icat_client, 889981)

    def test_raw_dataset_linkage_one_to_one(self, icat_client, internal_dataset_tasks, generate_raw_proc_datasets,
                                            create_raw_proc_datasets_relation):
        raw_dataset, proc_dataset = generate_raw_proc_datasets(1, 1)
        create_raw_proc_datasets_relation([raw_dataset], proc_dataset)

        internal_dataset_tasks.raw_dataset_linkage(icat_client, raw_dataset.id)

        input_dataset_param = get_dataset_parameter(icat_client, INPUT_DATASET_PARAMETER_NAME, dataset_id=proc_dataset.id)
        assert input_dataset_param.stringValue == raw_dataset.location
        input_dataset_ids_param = get_dataset_parameter(icat_client, INPUT_DATASET_IDS_PARAMETER_NAME, dataset_id=proc_dataset.id)
        assert input_dataset_ids_param.stringValue == str(raw_dataset.id)

        output_dataset_ids_param = get_dataset_parameter(icat_client, OUTPUT_DATASET_IDS_PARAMETER_NAME, dataset_id=raw_dataset.id)
        assert output_dataset_ids_param.stringValue == str(proc_dataset.id)
        output_dataset_names_param = get_dataset_parameter(icat_client, OUTPUT_DATASET_NAMES_PARAMETER_NAME, dataset_id=raw_dataset.id)
        assert output_dataset_names_param.stringValue == str(proc_dataset.name)


    def test_raw_dataset_linkage_one_to_many(self, icat_client, internal_dataset_tasks, generate_raw_proc_datasets,
                                            create_raw_proc_datasets_relation):
        raw_dataset, proc_datasets = generate_raw_proc_datasets(1, 3)
        for proc_dataset in proc_datasets:
            create_raw_proc_datasets_relation([raw_dataset], proc_dataset)

        internal_dataset_tasks.raw_dataset_linkage(icat_client, raw_dataset.id)

        for proc_dataset in proc_datasets:
            input_dataset_param = get_dataset_parameter(icat_client, INPUT_DATASET_PARAMETER_NAME, dataset_id=proc_dataset.id)
            assert input_dataset_param.stringValue == raw_dataset.location
            input_dataset_ids_param = get_dataset_parameter(icat_client, INPUT_DATASET_IDS_PARAMETER_NAME, dataset_id=proc_dataset.id)
            assert input_dataset_ids_param.stringValue == str(raw_dataset.id)

        output_dataset_ids_param = get_dataset_parameter(icat_client, OUTPUT_DATASET_IDS_PARAMETER_NAME, dataset_id=raw_dataset.id)
        assert output_dataset_ids_param.stringValue == " ".join(str(i.id) for i in proc_datasets)
        output_dataset_names_param = get_dataset_parameter(icat_client, OUTPUT_DATASET_NAMES_PARAMETER_NAME, dataset_id=raw_dataset.id)
        assert output_dataset_names_param.stringValue == " ".join(i.name for i in proc_datasets)

    def test_proc_dataset_linkage_one_to_one(self, icat_client, internal_dataset_tasks, generate_raw_proc_datasets,
                                             create_raw_proc_datasets_relation):
        raw_dataset, proc_dataset = generate_raw_proc_datasets(1, 1)
        create_raw_proc_datasets_relation([raw_dataset], proc_dataset)

        internal_dataset_tasks.processed_dataset_linkage(icat_client, proc_dataset.id)

        input_dataset_param = get_dataset_parameter(icat_client, INPUT_DATASET_PARAMETER_NAME, dataset_id=proc_dataset.id)
        assert input_dataset_param.stringValue == raw_dataset.location
        output_dataset_ids_param = get_dataset_parameter(icat_client, OUTPUT_DATASET_IDS_PARAMETER_NAME, dataset_id=raw_dataset.id)
        assert output_dataset_ids_param.stringValue == str(proc_dataset.id)
        output_dataset_names_param = get_dataset_parameter(icat_client, OUTPUT_DATASET_NAMES_PARAMETER_NAME, dataset_id=raw_dataset.id)
        assert output_dataset_names_param.stringValue == str(proc_dataset.name)

    def test_proc_dataset_linkage_many_to_one(self, icat_client, internal_dataset_tasks, generate_raw_proc_datasets,
                                             create_raw_proc_datasets_relation):
        raw_datasets, proc_dataset = generate_raw_proc_datasets(4, 1)
        create_raw_proc_datasets_relation(raw_datasets, proc_dataset)

        internal_dataset_tasks.processed_dataset_linkage(icat_client, proc_dataset.id)

        input_dataset_param = get_dataset_parameter(icat_client, INPUT_DATASET_PARAMETER_NAME, dataset_id=proc_dataset.id)
        assert input_dataset_param.stringValue == ",".join(i.location for i in raw_datasets)
        for raw_dataset in raw_datasets:
            output_dataset_ids_param = get_dataset_parameter(icat_client, OUTPUT_DATASET_IDS_PARAMETER_NAME, dataset_id=raw_dataset.id)
            assert output_dataset_ids_param.stringValue == str(proc_dataset.id)
            output_dataset_names_param = get_dataset_parameter(icat_client, OUTPUT_DATASET_NAMES_PARAMETER_NAME, dataset_id=raw_dataset.id)
            assert output_dataset_names_param.stringValue == proc_dataset.name