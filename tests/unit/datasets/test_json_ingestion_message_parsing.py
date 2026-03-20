import pytest

from exceptions.dataset import DatasetValidationError, DatasetDatafileLimitExceeded
from helpers.contexts.dataset import create_dataset_context
from helpers.static_settings import RAW_DATASET_TYPE_NAME, PROCESSED_DATASET_TYPE_NAME


@pytest.fixture
def invalid_json_payload(request):
    return request.getfixturevalue(request.param)


class TestJSONIngestionMessageParsing:

    def test_valid_raw_dataset_json_message(self, valid_json_raw_dataset_payload):
        dataset_ctx = create_dataset_context(valid_json_raw_dataset_payload)
        assert dataset_ctx.type == RAW_DATASET_TYPE_NAME

    def test_valid_json_raw_dataset_investigation_id_message(self, valid_json_raw_dataset_investigation_id_payload):
        dataset_ctx = create_dataset_context(valid_json_raw_dataset_investigation_id_payload)
        assert dataset_ctx.type == RAW_DATASET_TYPE_NAME

    def test_valid_json_processed_dataset_message(self, valid_json_processed_dataset_payload):
        dataset_ctx = create_dataset_context(valid_json_processed_dataset_payload)
        assert dataset_ctx.type == PROCESSED_DATASET_TYPE_NAME

    @pytest.mark.parametrize("invalid_json_payload",
                             [
                                 "json_message_missing_investigation",
                                 "json_message_missing_instrument",
                                 "json_message_missing_name",
                                 "json_message_missing_location",
                                 "json_message_missing_start_date",
                                 "json_message_missing_end_date",
                                 "json_message_missing_param_value",
                                 "json_message_missing_param_name",
                                 "json_message_empty_datafile_location",
                                 "json_message_empty_sample_name"
                             ],
                             indirect=True)
    def test_invalid_json_message(self, invalid_json_payload):
        with pytest.raises(DatasetValidationError):
            _ = create_dataset_context(invalid_json_payload)

    def test_enforce_sample_type_json_message(self, valid_json_raw_dataset_payload, monkeypatch):
        import globals_var

        ingestion_settings = {"dataset": {"mandatorySampleType": True}}

        monkeypatch.setattr(globals_var, "ingestion_settings", ingestion_settings)
        with pytest.raises(DatasetValidationError):
            _ = create_dataset_context(valid_json_raw_dataset_payload)

        valid_json_raw_dataset_payload["sample"]["type"] = "test"
        _ = create_dataset_context(valid_json_raw_dataset_payload)

    def test_enforce_datafile_specification_json_message(self, no_datafiles_json_raw_dataset_payload, monkeypatch):
        import globals_var

        ingestion_settings = {"dataset": {"automaticDatasetLocationIndex": False}}

        monkeypatch.setattr(globals_var, "ingestion_settings", ingestion_settings)
        with pytest.raises(DatasetValidationError):
            _ = create_dataset_context(no_datafiles_json_raw_dataset_payload)

    def test_enforce_datafile_location_check_json_message(self,
                                                          valid_json_raw_dataset_sketchy_datafile_location_payload,
                                                          monkeypatch):
        import globals_var

        ingestion_settings = {"dataset": {
            "checkAllowedLocationPaths": True,
            "allowedRootLocationPaths": ["/data"],
        }}

        monkeypatch.setattr(globals_var, "ingestion_settings", ingestion_settings)
        with pytest.raises(DatasetValidationError):
            _ = create_dataset_context(valid_json_raw_dataset_sketchy_datafile_location_payload)

    def test_enforce_dataset_location_check_json_message(self, valid_json_raw_dataset_sketchy_location_payload,
                                                         monkeypatch):
        import globals_var

        ingestion_settings = {
            "dataset": {
                "checkAllowedLocationPaths": True,
                "allowedRootLocationPaths": ["/tmp"],
                "mandatoryPathsExistence": True,
                "automaticDatasetLocationIndex": True
            }}

        monkeypatch.setattr(globals_var, "ingestion_settings", ingestion_settings)
        with pytest.raises(DatasetValidationError):
            _ = create_dataset_context(valid_json_raw_dataset_sketchy_location_payload)

    def test_enforce_max_datafiles_per_dataset(self, json_message_too_many_datafiles):
        with pytest.raises(DatasetDatafileLimitExceeded):
            _ = create_dataset_context(json_message_too_many_datafiles)

    def test_invalid_json_duplicate_parameters(self, json_message_duplicate_parameters):
        with pytest.raises(DatasetValidationError):
            _ = create_dataset_context(json_message_duplicate_parameters)
