import pytest

from exceptions.dataset import DatasetValidationError, DatasetDatafileLimitExceeded
from helpers.contexts.dataset import create_dataset_context
from helpers.static_settings import RAW_DATASET_TYPE_NAME, PROCESSED_DATASET_TYPE_NAME


@pytest.fixture
def invalid_xml_payload(request):
    return request.getfixturevalue(request.param)


class TestXMLIngestionMessageParsing:

    def test_valid_raw_dataset_xml_message(self, valid_xml_raw_dataset_payload):
        dataset_ctx = create_dataset_context(valid_xml_raw_dataset_payload)
        assert dataset_ctx.type == RAW_DATASET_TYPE_NAME

    def test_valid_xml_raw_dataset_investigation_id_message(self, valid_xml_raw_dataset_investigation_id_payload):
        dataset_ctx = create_dataset_context(valid_xml_raw_dataset_investigation_id_payload)
        assert dataset_ctx.type == RAW_DATASET_TYPE_NAME

    def test_valid_xml_processed_dataset_message(self, valid_xml_processed_dataset_payload):
        dataset_ctx = create_dataset_context(valid_xml_processed_dataset_payload)
        assert dataset_ctx.type == PROCESSED_DATASET_TYPE_NAME

    @pytest.mark.parametrize("invalid_xml_payload",
                             [
                                 "xml_message_missing_investigation",
                                 "xml_message_missing_instrument",
                                 "xml_message_missing_name",
                                 "xml_message_missing_location",
                                 "xml_message_missing_start_date",
                                 "xml_message_missing_end_date",
                                 "xml_message_missing_param_value",
                                 "xml_message_missing_param_name",
                                 "xml_message_empty_datafile_location",
                                 "xml_message_empty_sample_name"
                             ],
                             indirect=True)
    def test_invalid_xml_message(self, invalid_xml_payload):
        with pytest.raises(DatasetValidationError):
            _ = create_dataset_context(invalid_xml_payload)

    def test_enforce_sample_type_xml_message(self, valid_xml_raw_dataset_payload, monkeypatch,
                                             valid_xml_raw_dataset_payload_sample_type):
        import globals_var

        ingestion_settings = {"dataset": {"mandatorySampleType": True}}

        monkeypatch.setattr(globals_var, "ingestion_settings", ingestion_settings)
        with pytest.raises(DatasetValidationError):
            _ = create_dataset_context(valid_xml_raw_dataset_payload)

        _ = create_dataset_context(valid_xml_raw_dataset_payload_sample_type)

    def test_enforce_datafile_specification_xml_message(self, no_datafiles_xml_raw_dataset_payload, monkeypatch):
        import globals_var

        ingestion_settings = {"dataset": {"automaticDatasetLocationIndex": False}}

        monkeypatch.setattr(globals_var, "ingestion_settings", ingestion_settings)
        with pytest.raises(DatasetValidationError):
            _ = create_dataset_context(no_datafiles_xml_raw_dataset_payload)

    def test_enforce_datafile_location_check_xml_message(self, valid_xml_raw_dataset_sketchy_datafile_location_payload,
                                                         monkeypatch):
        import globals_var

        ingestion_settings = {"dataset": {
            "checkAllowedLocationPaths": True,
            "allowedRootLocationPaths": ["/data"],
        }}

        monkeypatch.setattr(globals_var, "ingestion_settings", ingestion_settings)
        with pytest.raises(DatasetValidationError):
            _ = create_dataset_context(valid_xml_raw_dataset_sketchy_datafile_location_payload)

    def test_enforce_dataset_location_check_xml_message(self, valid_xml_raw_dataset_sketchy_location_payload,
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
            _ = create_dataset_context(valid_xml_raw_dataset_sketchy_location_payload)

    def test_enforce_max_datafiles_per_dataset(self, xml_message_too_many_datafiles):
        with pytest.raises(DatasetDatafileLimitExceeded):
            _ = create_dataset_context(xml_message_too_many_datafiles)

    def test_invalid_xml_duplicate_parameters(self, xml_message_duplicate_parameters):
        with pytest.raises(DatasetValidationError):
            _ = create_dataset_context(xml_message_duplicate_parameters)
