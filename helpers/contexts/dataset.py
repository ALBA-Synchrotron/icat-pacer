import json
import os.path
from contextlib import suppress
from pathlib import Path

import xmltodict

import globals_var
from exceptions.dataset import DatasetValidationError, PayloadParsingError, DatasetDatafileLimitExceeded
from helpers.models.dataset import DatasetParameterContext, DatasetSampleContext, DatasetDatafileContext, \
    DatasetContext
from helpers.utils.xml import snakify_xml_dict_keys


def create_dataset_context(dataset_data: str | dict) -> DatasetContext:
    dataset_dict: dict
    dataset_ctx: DatasetContext

    ingestion_settings: dict = globals_var.ingestion_settings.get("dataset", {})

    transform_namespaces: dict = {i["schema"]: i["to"] for i in ingestion_settings.get("xmlNamespacesTransform", [])}

    if ingestion_settings.get("acceptXMLPayloads", True) and isinstance(dataset_data,
                                                                        str) and dataset_data.strip().endswith(">"):
        try:
            xml_payload = dataset_data.strip()
            dataset_dict = xmltodict.parse(xml_payload, process_namespaces=True, namespaces=transform_namespaces)[
                "dataset"]
            dataset_dict = snakify_xml_dict_keys(dataset_dict)
            if "parameter" in dataset_dict:
                dataset_dict["parameters"] = dataset_dict.pop("parameter")
            if "datafile" in dataset_dict:
                dataset_dict["datafiles"] = dataset_dict.pop("datafile")

        except Exception as e:
            raise PayloadParsingError(f"Error parsing XML payload: {e!r}", e)

    else:
        try:
            dataset_dict = json.loads(dataset_data) if isinstance(dataset_data, str) else dataset_data
        except Exception as e:
            raise PayloadParsingError(
                f"Error parsing JSON payload (XML is{' not' if not ingestion_settings.get("acceptXMLPayloads") else ''} accepted): {e!r}",
                e)

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

    return DatasetContext.model_validate({
        "investigation": investigation_name,
        "investigation_id": investigation_id,
        "instrument": instrument,
        "name": dataset_name,
        "parameters": [
            DatasetParameterContext.model_validate({"name": i.get("name", None), "value": i.get("value", None)}) for i
            in parameters if i],
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
        "sample": DatasetSampleContext.model_validate({"name": sample_name, "type": sample_type}),
        "datafiles": [DatasetDatafileContext.model_validate({"location": i.get("location", "")}) for i in datafiles if
                      i]}
    )
