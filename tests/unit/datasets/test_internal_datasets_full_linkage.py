import pytest

from exceptions.dataset import DatasetValidationError
from helpers.static_settings import FULL_INPUT_DATASET_IDS_PARAMETER_NAME, FULL_INPUT_DATASET_NAMES_PARAMETER_NAME, \
    OUTPUT_DATASET_IDS_PARAMETER_NAME, OUTPUT_DATASET_NAMES_PARAMETER_NAME, FULL_OUTPUT_DATASET_IDS_PARAMETER_NAME, \
    FULL_OUTPUT_DATASET_NAMES_PARAMETER_NAME


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

    def test_build_dataset_full_links_information_1(self, icat_client, internal_dataset_tasks,
                                                    internal_dataset_links_tasks,
                                                    generate_raw_proc_datasets,
                                                    create_raw_proc_datasets_relation):
        """
        Scenario:
        [raw_1] ─┐
        [raw_2] ─┼
        [raw_3] ─┼──► [proc_1] ───► [proc_2]
        [raw_4] ─┘
        """

        raw_datasets, proc_dataset_1 = generate_raw_proc_datasets(4, 1)
        _, proc_dataset_2 = generate_raw_proc_datasets(0, 1)
        create_raw_proc_datasets_relation(raw_datasets, proc_dataset_1)
        create_raw_proc_datasets_relation(proc_dataset_1, proc_dataset_2)

        internal_dataset_tasks.processed_dataset_linkage(icat_client, proc_dataset_1.id)
        internal_dataset_tasks.processed_dataset_linkage(icat_client, proc_dataset_2.id)

        for dataset in [proc_dataset_1, proc_dataset_2, *raw_datasets]:
            internal_dataset_links_tasks.build_dataset_full_links_information(icat_client, dataset.id)

        # proc_dataset_1
        proc_dataset_1 = icat_client.search("Dataset", conditions={"id__eq": proc_dataset_1.id}, flatten_single=True)
        proc_params = [(str(i.type.name), str(i.stringValue)) for i in proc_dataset_1.parameters]
        ids_value = next(v for k, v in proc_params if k == FULL_INPUT_DATASET_IDS_PARAMETER_NAME)
        assert set(ids_value.split()) == {str(i.id) for i in raw_datasets}
        names_value = next(v for k, v in proc_params if k == FULL_INPUT_DATASET_NAMES_PARAMETER_NAME)
        assert set(names_value.split()) == {i.name for i in raw_datasets}

        assert (FULL_OUTPUT_DATASET_IDS_PARAMETER_NAME, str(proc_dataset_2.id)) in proc_params
        assert (FULL_OUTPUT_DATASET_NAMES_PARAMETER_NAME, str(proc_dataset_2.name)) in proc_params

        # proc_dataset_2
        proc_dataset_2 = icat_client.search("Dataset", conditions={"id__eq": proc_dataset_2.id}, flatten_single=True)
        proc_params = [(str(i.type.name), str(i.stringValue)) for i in proc_dataset_2.parameters]
        ids_value = next(v for k, v in proc_params if k == FULL_INPUT_DATASET_IDS_PARAMETER_NAME)
        assert set(ids_value.split()) == {str(i.id) for i in [*raw_datasets, proc_dataset_1]}
        names_value = next(v for k, v in proc_params if k == FULL_INPUT_DATASET_NAMES_PARAMETER_NAME)
        assert set(names_value.split()) == {i.name for i in [*raw_datasets, proc_dataset_1]}

        # raw_dataset_N
        for raw_dataset in raw_datasets:
            dataset = icat_client.search("Dataset", conditions={"id__eq": raw_dataset.id}, flatten_single=True)
            raw_params = [(str(i.type.name), str(i.stringValue)) for i in dataset.parameters]
            ids_value = next(v for k, v in raw_params if k == FULL_OUTPUT_DATASET_IDS_PARAMETER_NAME)
            assert set(ids_value.split()) == {str(i.id) for i in [proc_dataset_1, proc_dataset_2]}
            names_value = next(v for k, v in raw_params if k == FULL_OUTPUT_DATASET_NAMES_PARAMETER_NAME)
            assert set(names_value.split()) == {i.name for i in [proc_dataset_1, proc_dataset_2]}

    def test_build_dataset_full_links_information_2(self, icat_client, internal_dataset_tasks,
                                                    internal_dataset_links_tasks,
                                                    generate_raw_proc_datasets,
                                                    create_raw_proc_datasets_relation):
        """
        Scenario:
        [raw_1] ─┐
                 ┼──► [proc_1]─┐
        [raw_2] ─┘             ├── [proc_3]
        [raw_3] ─┐─────────────┘
                 ┼──► [proc_2]
        [raw_4] ─┘
        """

        raw_datasets, proc_dataset_1 = generate_raw_proc_datasets(4, 1)
        _, proc_dataset_2 = generate_raw_proc_datasets(0, 1)
        _, proc_dataset_3 = generate_raw_proc_datasets(0, 1)
        create_raw_proc_datasets_relation(raw_datasets[:2], proc_dataset_1)
        create_raw_proc_datasets_relation(raw_datasets[2:], proc_dataset_2)
        create_raw_proc_datasets_relation([raw_datasets[2], proc_dataset_1], proc_dataset_3)

        internal_dataset_tasks.processed_dataset_linkage(icat_client, proc_dataset_1.id)
        internal_dataset_tasks.processed_dataset_linkage(icat_client, proc_dataset_2.id)
        internal_dataset_tasks.processed_dataset_linkage(icat_client, proc_dataset_3.id)

        for dataset in [*raw_datasets, proc_dataset_1, proc_dataset_2, proc_dataset_3]:
            internal_dataset_links_tasks.build_dataset_full_links_information(icat_client, dataset.id)

        # proc_dataset_1
        proc_dataset_1 = icat_client.search("Dataset", conditions={"id__eq": proc_dataset_1.id}, flatten_single=True)
        proc_params = [(str(i.type.name), str(i.stringValue)) for i in proc_dataset_1.parameters]
        ids_value = next(v for k, v in proc_params if k == FULL_INPUT_DATASET_IDS_PARAMETER_NAME)
        assert set(ids_value.split()) == {str(i.id) for i in raw_datasets[:2]}
        names_value = next(v for k, v in proc_params if k == FULL_INPUT_DATASET_NAMES_PARAMETER_NAME)
        assert set(names_value.split()) == {i.name for i in raw_datasets[:2]}

        assert (FULL_OUTPUT_DATASET_IDS_PARAMETER_NAME, str(proc_dataset_3.id)) in proc_params
        assert (FULL_OUTPUT_DATASET_NAMES_PARAMETER_NAME, str(proc_dataset_3.name)) in proc_params

        # proc_dataset_2
        proc_dataset_2 = icat_client.search("Dataset", conditions={"id__eq": proc_dataset_2.id}, flatten_single=True)
        proc_params = [(str(i.type.name), str(i.stringValue)) for i in proc_dataset_2.parameters]
        ids_value = next(v for k, v in proc_params if k == FULL_INPUT_DATASET_IDS_PARAMETER_NAME)
        assert set(ids_value.split()) == {str(i.id) for i in raw_datasets[2:]}
        names_value = next(v for k, v in proc_params if k == FULL_INPUT_DATASET_NAMES_PARAMETER_NAME)
        assert set(names_value.split()) == {i.name for i in raw_datasets[2:]}

        # proc_dataset_3
        proc_dataset_3 = icat_client.search("Dataset", conditions={"id__eq": proc_dataset_3.id}, flatten_single=True)
        proc_params = [(str(i.type.name), str(i.stringValue)) for i in proc_dataset_3.parameters]
        ids_value = next(v for k, v in proc_params if k == FULL_INPUT_DATASET_IDS_PARAMETER_NAME)
        assert set(ids_value.split()) == {str(i.id) for i in [*raw_datasets[:3], proc_dataset_1]}
        names_value = next(v for k, v in proc_params if k == FULL_INPUT_DATASET_NAMES_PARAMETER_NAME)
        assert set(names_value.split()) == {i.name for i in [*raw_datasets[:3], proc_dataset_1]}

        # raw_dataset_1 and raw_dataset_2
        datasets = raw_datasets[:2]
        for dataset in datasets:
            raw_dataset = icat_client.search("Dataset", conditions={"id__eq": dataset.id}, flatten_single=True)
            raw_params = [(str(i.type.name), str(i.stringValue)) for i in raw_dataset.parameters]
            ids_value = next(v for k, v in raw_params if k == FULL_OUTPUT_DATASET_IDS_PARAMETER_NAME)
            assert set(ids_value.split()) == {str(i.id) for i in [proc_dataset_1, proc_dataset_3]}
            names_value = next(v for k, v in raw_params if k == FULL_OUTPUT_DATASET_NAMES_PARAMETER_NAME)
            assert set(names_value.split()) == {i.name for i in [proc_dataset_1, proc_dataset_3]}

        # raw_dataset_3
        raw_dataset_3 = icat_client.search("Dataset", conditions={"id__eq": raw_datasets[2].id}, flatten_single=True)
        raw_params = [(str(i.type.name), str(i.stringValue)) for i in raw_dataset_3.parameters]
        ids_value = next(v for k, v in raw_params if k == FULL_OUTPUT_DATASET_IDS_PARAMETER_NAME)
        assert set(ids_value.split()) == {str(i.id) for i in [proc_dataset_2, proc_dataset_3]}
        names_value = next(v for k, v in raw_params if k == FULL_OUTPUT_DATASET_NAMES_PARAMETER_NAME)
        assert set(names_value.split()) == {i.name for i in [proc_dataset_2, proc_dataset_3]}

        # raw_dataset_4
        raw_dataset_4 = icat_client.search("Dataset", conditions={"id__eq": raw_datasets[3].id}, flatten_single=True)
        raw_params = [(str(i.type.name), str(i.stringValue)) for i in raw_dataset_4.parameters]
        ids_value = next(v for k, v in raw_params if k == FULL_OUTPUT_DATASET_IDS_PARAMETER_NAME)
        assert set(ids_value.split()) == {str(i.id) for i in [proc_dataset_2]}
        names_value = next(v for k, v in raw_params if k == FULL_OUTPUT_DATASET_NAMES_PARAMETER_NAME)
        assert set(names_value.split()) == {i.name for i in [proc_dataset_2]}