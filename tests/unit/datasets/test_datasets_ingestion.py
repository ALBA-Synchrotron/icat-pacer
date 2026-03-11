import pytest

from exceptions.instrument import InstrumentNotFound
from exceptions.investigation import InvestigationNotFound, InvestigationInstrumentMismatch
from exceptions.sample import SampleTypeNotFound
from helpers.contexts.dataset import create_dataset_context


@pytest.fixture
def dataset_msg(request):
    return request.getfixturevalue(request.param)


class TestDatasetsConsumer:

    @pytest.mark.parametrize("dataset_msg", [
        "xml_dataset_non_existent_instrument",
        "json_dataset_non_existent_instrument"
    ], indirect=True)
    def test_create_dataset_non_existent_instrument(self, dataset_tasks, icat_client, dataset_msg):
        dataset_ctx = create_dataset_context(dataset_msg)
        with pytest.raises(InstrumentNotFound):
            _, _, _ = dataset_tasks.create_base_dataset_icat(icat_client=icat_client, dataset_ctx=dataset_ctx)

    @pytest.mark.parametrize("dataset_msg", [
        "xml_dataset_non_existent_investigation",
        "json_dataset_non_existent_investigation"
    ], indirect=True)
    def test_create_dataset_non_existent_investigation(self, dataset_tasks, icat_client, dataset_msg):
        dataset_ctx = create_dataset_context(dataset_msg)
        with pytest.raises(InvestigationNotFound):
            _, _, _ = dataset_tasks.create_base_dataset_icat(icat_client=icat_client, dataset_ctx=dataset_ctx)

    @pytest.mark.parametrize("dataset_msg", [
        "xml_raw_dataset_investigation_instrument_mismatch",
        "json_raw_dataset_investigation_instrument_mismatch"
    ], indirect=True)
    def test_create_dataset_investigation_instrument_mismatch(self, dataset_tasks, icat_client, dataset_msg):
        dataset_ctx = create_dataset_context(dataset_msg)
        with pytest.raises(InvestigationInstrumentMismatch):
            _, _, _ = dataset_tasks.create_base_dataset_icat(icat_client=icat_client, dataset_ctx=dataset_ctx)

    @pytest.mark.parametrize("dataset_msg", [
        "xml_raw_dataset_invalid_sample_type",
        "json_raw_dataset_invalid_sample_type"
    ], indirect=True)
    def test_create_dataset_invalid_sample_type(self, dataset_tasks, icat_client, dataset_msg):
        dataset_ctx = create_dataset_context(dataset_msg)
        with pytest.raises(SampleTypeNotFound):
            _, _, _ = dataset_tasks.create_base_dataset_icat(icat_client=icat_client, dataset_ctx=dataset_ctx)

    @pytest.mark.skip(reason="Not implemented yet")
    def test_ingest_duplicate_raw_dataset(self):
        # TODO: Should change its name with the current date as suffix
        pass

    @pytest.mark.skip(reason="Not implemented yet")
    def test_create_dataset_instrument_mismatch_investigation_id(self):
        pass

    @pytest.mark.skip(reason="Not implemented yet")
    def test_create_dataset_multiple_investigation_collision(self):
        pass

    @pytest.mark.skip(reason="Not implemented yet")
    def test_ingest_duplicate_proc_dataset(self):
        # TODO: Specific handler in tasks/datasets.py, line 26
        pass