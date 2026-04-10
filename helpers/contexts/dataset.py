import json
import os.path
from contextlib import suppress
from pathlib import Path

import xmltodict

import globals_var
from exceptions.dataset import DatasetValidationError, PayloadParsingError, DatasetDatafileLimitExceeded
from helpers.dataclasses.dataset import DatasetParameterContext, DatasetSampleContext, DatasetDatafileContext, \
    DatasetContext
from helpers.static_settings import INPUT_DATASET_PARAMETER_NAME, PROCESSED_DATASET_TYPE_NAME, RAW_DATASET_TYPE_NAME


def create_dataset_context(dataset_data: str | dict) -> DatasetContext:
    dataset_dict: dict
    dataset_ctx: DatasetContext

    ingestion_settings: dict = globals_var.ingestion_settings.get("dataset", {})


    transform_namespaces: dict = {i["schema"]: i["to"] for i in ingestion_settings.get("xmlNamespacesTransform", [])}

    if ingestion_settings.get("acceptXMLPayloads", True) and isinstance(dataset_data,
                                                                        str) and dataset_data.strip().endswith(">"):
        try:
            xml_payload = dataset_data.strip()
            dataset_dict = xmltodict.parse(xml_payload, process_namespaces=True, namespaces=transform_namespaces)["dataset"]
            if "datafile" in dataset_dict:
                dataset_dict["datafiles"] = dataset_dict["datafile"]
            if "parameter" in dataset_dict:
                dataset_dict["parameters"] = dataset_dict["parameter"]
            dataset_dict["start_date"] = dataset_dict["startDate"]
            dataset_dict["end_date"] = dataset_dict["endDate"]
            if "investigationId" in dataset_dict:
                dataset_dict["investigation_id"] = int(dataset_dict["investigationId"])
        except Exception as e:
            raise PayloadParsingError(f"Error parsing XML payload: {e!r}", e)

    else:
        try:
            dataset_dict = json.loads(dataset_data) if isinstance(dataset_data, str) else dataset_data
        except Exception as e:
            raise PayloadParsingError(
                f"Error parsing JSON payload (XML is{' not' if not ingestion_settings.get("acceptXMLPayloads") else ''} accepted): {e!r}", e)

    investigation_name: str = dataset_dict.get("investigation", "")
    investigation_id: int = dataset_dict.get("investigation_id", 0)
    instrument: str = dataset_dict.get("instrument", "")
    dataset_name: str = dataset_dict.get("name", "")
    parameters: list = dataset_dict.get("parameters", []) if isinstance(dataset_dict.get("parameters"), list) else [
        dataset_dict.get("parameters")]
    location: str = dataset_dict.get("location", "")
    start_date: str = dataset_dict.get("start_date", "")
    end_date: str = dataset_dict.get("end_date", "")
    sample: dict = dataset_dict.get("sample", {})

    if not sample:
        raise PayloadParsingError(f"Sample information is missing in dataset payload: {dataset_dict!r}")

    sample_name: str = sample.get("name", "")
    sample_type: str = sample.get("type", "")
    datafiles: list = dataset_dict.get("datafiles", []) if isinstance(dataset_dict.get("datafiles"), list) else [
        dataset_dict.get("datafiles")]

    dataset_ctx = DatasetContext(
        investigation=investigation_name,
        investigation_id=investigation_id,
        instrument=instrument,
        name=dataset_name,
        parameters=[DatasetParameterContext(name=i.get("name", None), value=i.get("value", None)) for i in parameters if i],
        location=location,
        start_date=start_date,
        end_date=end_date,
        sample=DatasetSampleContext(name=sample_name, type=sample_type),
        datafiles=[DatasetDatafileContext(location=i.get("location", "")) for i in datafiles if i],
    )

    # Dynamic validations
    if INPUT_DATASET_PARAMETER_NAME in [i.name for i in dataset_ctx.parameters]:
        dataset_ctx.type = PROCESSED_DATASET_TYPE_NAME
    else:
        dataset_ctx.type = RAW_DATASET_TYPE_NAME

    if not dataset_ctx.sample.type and ingestion_settings.get("mandatorySampleType"):
        raise DatasetValidationError("Sample type not found in payload.")

    if not ingestion_settings.get("automaticDatasetLocationIndex") and not dataset_ctx.datafiles:
        raise DatasetValidationError("No datafiles found in payload.")

    if ingestion_settings.get("checkAllowedLocationPaths"):
        strict_checking: bool = ingestion_settings.get("mandatoryPathsExistence", False)
        allowed_root_locations: list = ingestion_settings.get("allowedRootLocationPaths", [])

        def is_df_location_in_allowed_roots(path: str) -> bool:
            with suppress(OSError):
                df_location: Path = Path(path).resolve(strict=strict_checking)
                for allowed_root_path in allowed_root_locations:
                    if df_location.is_relative_to(allowed_root_path):
                        return True
            return False

        if not all(is_df_location_in_allowed_roots(i.location) for i in dataset_ctx.datafiles):
            raise DatasetValidationError(
                f"Datafile location(s) outside of allowed root location(s), valid root are: {",".join(allowed_root_locations)}")

        if not is_df_location_in_allowed_roots(dataset_ctx.location):
            raise DatasetValidationError(
                f"Dataset location outside of allowed root location(s), valid root are: {",".join(allowed_root_locations)}")

    # Avoid double file existence check if strict check / resolution has been done before.
    if ingestion_settings.get("mandatoryPathsExistence") and not ingestion_settings.get("checkAllowedLocationPaths"):
        if not os.path.exists(location):
            raise DatasetValidationError(f"Dataset root location does not exist: {location}")

        for datafile in dataset_ctx.datafiles:
            if not os.path.exists(datafile.location):
                raise DatasetValidationError(f"Dataset's datafile root location does not exist: {datafile.location}")

    if len(dataset_ctx.datafiles) > ingestion_settings.get("maxDatafilesPerDataset", 30000):
        raise DatasetDatafileLimitExceeded(
            f"Too many datafiles ({len(dataset_ctx.datafiles)}) in dataset, ingestion rejected due to limit exceeded")

    param_names = [i.name for i in dataset_ctx.parameters]
    if len(param_names) != len(set(param_names)):
        raise DatasetValidationError(f"Duplicate parameter names found in dataset: {param_names}")

    return dataset_ctx
