import json
import os.path

import xmltodict

from helpers.dataclasses.dataset import DatasetParameterContext, DatasetSampleContext, DatasetDatafileContext, \
    DatasetContext


def create_dataset_context(dataset_data: str | dict, ingestion_settings: dict) -> DatasetContext:
    dataset_dict: dict
    dataset_ctx: DatasetContext

    if ingestion_settings.get("acceptXMLPayloads") and isinstance(dataset_data, str):
        try:
            dataset_dict = xmltodict.parse(dataset_data)["dataset"]
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
    parameters: list = dataset_dict.get("parameter", []) if isinstance(dataset_dict.get("parameter"), list) else [
        dataset_dict.get("parameter")]
    location: str = dataset_dict.get("location", "")
    start_date: str = dataset_dict.get("startDate", "")
    end_date: str = dataset_dict.get("endDate", "")
    sample: dict = dataset_dict.get("sample", {})
    sample_name: str = sample.get("name", "")
    sample_type: str = sample.get("type", "")
    datafiles: list = dataset_dict.get("datafile", []) if isinstance(dataset_dict.get("datafile"), list) else [
        dataset_dict.get("datafile")]

    dataset_ctx = DatasetContext(
        investigation=investigation_name,
        instrument=instrument,
        name=dataset_name,
        parameters=[DatasetParameterContext(name=i.get("name", ""), value=i.get("value", "")) for i in parameters],
        location=location,
        start_date=start_date,
        end_date=end_date,
        sample=DatasetSampleContext(name=sample_name, type=sample_type),
        datafiles=[DatasetDatafileContext(location=i.get("location", "")) for i in datafiles]
    )

    # Dynamic validations
    if not dataset_ctx.sample.type and ingestion_settings.get("mandatorySampleType"):
        raise ValueError("Sample type not found in payload.")

    if ingestion_settings.get("mandatoryPathsExistence"):
        if not os.path.exists(location):
            raise ValueError(f"Dataset root location does not exist: {location}")

        for datafile in dataset_ctx.datafiles:
            if not os.path.exists(datafile.location):
                raise ValueError(f"Dataset root location does not exist: {datafile.location}")

    return dataset_ctx
