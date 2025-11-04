import json
import os.path
from pathlib import Path

import xmltodict

from helpers.dataclasses.dataset import DatasetParameterContext, DatasetSampleContext, DatasetDatafileContext, \
    DatasetContext
from helpers.static_settings import INPUT_DATASET_PARAMETER_NAME, PROCESSED_DATASET_TYPE_NAME, RAW_DATASET_TYPE_NAME


def create_dataset_context(dataset_data: str | dict, ingestion_settings: dict) -> DatasetContext:
    dataset_dict: dict
    dataset_ctx: DatasetContext

    if ingestion_settings.get("acceptXMLPayloads") and isinstance(dataset_data, str) and dataset_data.endswith(">"):
        try:
            dataset_dict = xmltodict.parse(dataset_data)["dataset"]
            dataset_dict["datafiles"] = dataset_dict["datafile"]
            dataset_dict["parameters"] = dataset_dict["parameter"]
            dataset_dict["start_date"] = dataset_dict["startDate"]
            dataset_dict["end_date"] = dataset_dict["endDate"]
        except Exception as e:
            raise ValueError(f"Error parsing XML payload: {e!r}")

    else:
        try:
            dataset_dict = json.loads(dataset_data) if isinstance(dataset_data, str) else dataset_data
        except Exception as e:
            raise ValueError(
                f"Error parsing JSON payload (XML is{' not' if not ingestion_settings.get("acceptXMLPayloads") else ''} accepted): {e!r}")

    investigation_name: str = dataset_dict.get("investigation", "")
    instrument: str = dataset_dict.get("instrument", "")
    dataset_name: str = dataset_dict.get("name", "")
    parameters: list = dataset_dict.get("parameters", []) if isinstance(dataset_dict.get("parameters"), list) else [
        dataset_dict.get("parameters")]
    location: str = dataset_dict.get("location", "")
    start_date: str = dataset_dict.get("start_date", "")
    end_date: str = dataset_dict.get("end_date", "")
    sample: dict = dataset_dict.get("sample", {})
    sample_name: str = sample.get("name", "")
    sample_type: str = sample.get("type", "")
    datafiles: list = dataset_dict.get("datafiles", []) if isinstance(dataset_dict.get("datafiles"), list) else [
        dataset_dict.get("datafiles")]

    dataset_ctx = DatasetContext(
        investigation=investigation_name,
        instrument=instrument,
        name=dataset_name,
        parameters=[DatasetParameterContext(name=i.get("name", ""), value=i.get("value", "")) for i in parameters],
        location=location,
        start_date=start_date,
        end_date=end_date,
        sample=DatasetSampleContext(name=sample_name, type=sample_type),
        datafiles=[DatasetDatafileContext(location=i.get("location", "")) for i in datafiles],
    )

    # Dynamic validations
    if INPUT_DATASET_PARAMETER_NAME in [i.name for i in dataset_ctx.parameters]:
        dataset_ctx.type = PROCESSED_DATASET_TYPE_NAME
    else:
        dataset_ctx.type = RAW_DATASET_TYPE_NAME

    if not dataset_ctx.sample.type and ingestion_settings.get("mandatorySampleType"):
        raise ValueError("Sample type not found in payload.")

    if ingestion_settings.get("checkAllowedLocationPaths"):
        strict_checking: bool = ingestion_settings.get("mandatoryPathsExistence", False)
        allowed_root_locations: list = ingestion_settings.get("allowedRootLocationPaths", [])

        def is_df_location_in_allowed_roots(path: str) -> bool:
            try:
                df_location: Path = Path(path).resolve(strict=strict_checking)
                for allowed_root_path in allowed_root_locations:
                    if df_location.is_relative_to(allowed_root_path):
                        return True
            except OSError:
                pass
            return False

        if not all(is_df_location_in_allowed_roots(i.location) for i in dataset_ctx.datafiles):
            raise ValueError(
                f"Datafile location(s) outside of allowed root location(s), valid root are: {",".join(allowed_root_locations)}")

    # Avoid double file existence check if strict check / resolution has been done before.
    if ingestion_settings.get("mandatoryPathsExistence") and not ingestion_settings.get("checkAllowedLocationPaths"):
        if not os.path.exists(location):
            raise ValueError(f"Dataset root location does not exist: {location}")

        for datafile in dataset_ctx.datafiles:
            if not os.path.exists(datafile.location):
                raise ValueError(f"Dataset root location does not exist: {datafile.location}")

    return dataset_ctx
