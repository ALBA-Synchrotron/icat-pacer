import pytest

from exceptions.dataset import DatasetNotFound, DatasetValidationError
from helpers.static_settings import DATASET_NAME_PARAMETER, DATASET_FILE_COUNT_PARAMETER, DATASET_VOLUME_PARAMETER, \
    DATASET_ELAPSE_TIME_PARAMETER, INVESTIGATION_DATASET_COUNT_PARAMETER, \
    INVESTIGATION_ACQUISITION_DATASET_COUNT_PARAMETER, RAW_DATASET_TYPE_NAME, \
    INVESTIGATION_PROCESSED_DATASET_COUNT_PARAMETER
from helpers.utils.dataset import get_dataset_parameter
from helpers.utils.investigation import get_investigation_parameter


@pytest.fixture
def dataset_msg(request):
    return request.getfixturevalue(request.param)


class TestInternalStatisticsConsumer:

    def test_update_dataset_statistics_missing_dataset_id(self, internal_statistics_tasks, icat_client):
        with pytest.raises(DatasetValidationError):
            internal_statistics_tasks.update_dataset_statistics(icat_client, None)

    def test_update_dataset_statistics_non_existing_dataset(self, internal_statistics_tasks, icat_client):
        with pytest.raises(DatasetNotFound):
            internal_statistics_tasks.update_dataset_statistics(icat_client, 9999999)

    def test_update_dataset_statistics(self, internal_statistics_tasks, icat_client, generate_raw_proc_datasets):
        raw_datasets, _ = generate_raw_proc_datasets(7, 0, 4)
        for raw_dataset in raw_datasets:
            internal_statistics_tasks.update_dataset_statistics(icat_client, raw_dataset.id)

            dataset_name_param = get_dataset_parameter(icat_client, DATASET_NAME_PARAMETER, entity=raw_dataset)
            assert dataset_name_param.stringValue == raw_dataset.name
            filecount_param = get_dataset_parameter(icat_client, DATASET_FILE_COUNT_PARAMETER, entity=raw_dataset)

            assert filecount_param.stringValue == str(len(raw_dataset.datafiles))
            volume_param = get_dataset_parameter(icat_client, DATASET_VOLUME_PARAMETER, entity=raw_dataset)

            assert volume_param.stringValue == str(sum(i.fileSize for i in raw_dataset.datafiles))
            elapsed_time_param = get_dataset_parameter(icat_client, DATASET_ELAPSE_TIME_PARAMETER, entity=raw_dataset)
            assert elapsed_time_param.stringValue == str(
                int((raw_dataset.endDate - raw_dataset.startDate).total_seconds()))

    def test_update_investigation_statistics_missing_dataset_id(self, internal_statistics_tasks, icat_client):
        with pytest.raises(DatasetValidationError):
            internal_statistics_tasks.update_investigation_statistics(icat_client, None)

    def test_update_investigation_statistics_non_existing_dataset(self, internal_statistics_tasks, icat_client):
        with pytest.raises(DatasetNotFound):
            internal_statistics_tasks.update_investigation_statistics(icat_client, 9999999)

    def test_update_investigation_statistics(self, internal_statistics_tasks, icat_client, generate_raw_proc_datasets):
        raw_datasets, proc_datasets = generate_raw_proc_datasets(3, 2, 4)
        investigation = raw_datasets[0].investigation

        for raw_dataset in raw_datasets + proc_datasets:
            internal_statistics_tasks.update_dataset_statistics(icat_client, raw_dataset.id)
        internal_statistics_tasks.update_investigation_statistics(icat_client, raw_datasets[0].id)

        dataset_count_param = get_investigation_parameter(icat_client, INVESTIGATION_DATASET_COUNT_PARAMETER,
                                                          entity=investigation)
        assert dataset_count_param.stringValue == str(len(raw_datasets) + len(proc_datasets))

        acq_dataset_count_param = get_investigation_parameter(icat_client,
                                                              INVESTIGATION_ACQUISITION_DATASET_COUNT_PARAMETER,
                                                              entity=investigation)
        assert acq_dataset_count_param.stringValue == str(len(raw_datasets))

        proc_dataset_count_param = get_investigation_parameter(icat_client,
                                                               INVESTIGATION_PROCESSED_DATASET_COUNT_PARAMETER,
                                                               entity=investigation)
        assert proc_dataset_count_param.stringValue == str(len(proc_datasets))

