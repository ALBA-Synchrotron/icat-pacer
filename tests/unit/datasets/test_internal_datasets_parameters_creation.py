import pytest

from exceptions.dataset import DatasetValidationError, DatasetNotFound
from exceptions.parameter import ParameterTypeNotFound
from helpers.contexts.dataset import create_dataset_context
from helpers.dataclasses.dataset import DatasetParameterContext
from helpers.static_settings import DATASET_PROCESSING_VERSION_PARAMETER_NAME


@pytest.fixture
def dataset_msg(request):
    return request.getfixturevalue(request.param)


class TestInternalDatasetConsumerDatasetParameterCreation:

    @pytest.mark.parametrize("dataset_msg", [
        "xml_raw_dataset",
        "json_raw_dataset",
    ], indirect=True)
    def test_create_parameters_dataset_id_not_provided(self, internal_dataset_tasks, icat_client, dataset_msg):
        dataset_ctx = create_dataset_context(dataset_msg)
        with pytest.raises(DatasetValidationError):
            internal_dataset_tasks.create_dataset_parameters(icat_client, dataset_ctx, 0, False)

    @pytest.mark.parametrize("dataset_msg", [
        "xml_raw_dataset",
        "json_raw_dataset",
    ], indirect=True)
    def test_create_datafiles_non_existent_dataset(self, internal_dataset_tasks, icat_client, dataset_msg):
        dataset_ctx = create_dataset_context(dataset_msg)
        with pytest.raises(DatasetNotFound):
            internal_dataset_tasks.create_dataset_parameters(icat_client, dataset_ctx, 99827, False)

    @pytest.mark.parametrize("dataset_msg", [
        "xml_raw_dataset",
        "json_raw_dataset",
    ], indirect=True)
    def test_create_parameters(self, dataset_tasks, internal_dataset_tasks, icat_client, dataset_msg):
        dataset_ctx = create_dataset_context(dataset_msg)
        new_dataset_id, investigation_id, is_duplicated = dataset_tasks.create_base_dataset_icat(
            icat_client=icat_client, dataset_ctx=dataset_ctx)
        internal_dataset_tasks.create_dataset_parameters(icat_client, dataset_ctx, new_dataset_id, is_duplicated)

        dataset = icat_client.search("Dataset", conditions={"id__eq": new_dataset_id}, flatten_single=True)
        assert len(dataset.parameters) == len(dataset_ctx.parameters)
        dataset_params = [(i.type.name, i.stringValue) for i in dataset.parameters]
        ctx_params = [(i.name, i.value) for i in dataset_ctx.parameters]
        assert set(dataset_params) == set(ctx_params)

    @pytest.mark.parametrize("dataset_msg", [
        "xml_raw_dataset",
        "json_raw_dataset",
    ], indirect=True)
    def test_create_parameters_non_existent_parameter_type(self, dataset_tasks, internal_dataset_tasks, icat_client, dataset_msg):
        dataset_ctx = create_dataset_context(dataset_msg)
        new_dataset_id, investigation_id, is_duplicated = dataset_tasks.create_base_dataset_icat(
            icat_client=icat_client, dataset_ctx=dataset_ctx)
        dataset_ctx.name = f"{dataset_ctx.name}-non-existent-param-type"
        dataset_ctx.parameters[-1].name = "just_invented"
        with pytest.raises(ParameterTypeNotFound):
            internal_dataset_tasks.create_dataset_parameters(icat_client, dataset_ctx, new_dataset_id, is_duplicated)

    @pytest.mark.parametrize("dataset_msg", [
        "xml_proc_dataset",
        "json_proc_dataset",
    ], indirect=True)
    def test_parameter_metadata_overwrite(self, dataset_tasks, internal_dataset_tasks, icat_client, dataset_msg):
        dataset_ctx = create_dataset_context(dataset_msg)
        new_dataset_id, investigation_id, is_duplicated = dataset_tasks.create_base_dataset_icat(
            icat_client=icat_client, dataset_ctx=dataset_ctx)
        internal_dataset_tasks.create_dataset_parameters(icat_client, dataset_ctx, new_dataset_id, is_duplicated)

        dataset  = icat_client.search("Dataset", conditions={"id__eq": new_dataset_id}, flatten_single=True)
        assert len(dataset.parameters) == len(dataset_ctx.parameters)

        dataset_ctx.parameters.append(DatasetParameterContext("parameter_type_2", "no"))
        new_dataset_id, investigation_id, is_duplicated = dataset_tasks.create_base_dataset_icat(
            icat_client=icat_client, dataset_ctx=dataset_ctx)
        internal_dataset_tasks.create_dataset_parameters(icat_client, dataset_ctx, new_dataset_id, is_duplicated)
        assert is_duplicated
        assert "parameter_type_2" not in [i.type.name for i in dataset.parameters]

        dataset_ctx.parameters.append(DatasetParameterContext(DATASET_PROCESSING_VERSION_PARAMETER_NAME, "2"))

        internal_dataset_tasks.create_dataset_parameters(icat_client, dataset_ctx, new_dataset_id, is_duplicated)
        dataset  = icat_client.search("Dataset", conditions={"id__eq": new_dataset_id}, flatten_single=True)
        params = [(i.type.name, i.stringValue) for i in dataset.parameters]
        assert ("parameter_type_2", "no") in params
        assert (DATASET_PROCESSING_VERSION_PARAMETER_NAME, "2") in params
