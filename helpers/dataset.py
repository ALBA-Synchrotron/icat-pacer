import json

import xmltodict

from helpers.dataclasses import DatasetContext


def create_dataset_context(dataset_data: str or dict, accept_xml_payload: bool) -> DatasetContext:
    dataset_dict: dict

    if accept_xml_payload:
        try:
            dataset_dict = xmltodict.parse(dataset_data)["investigation"]
        except Exception as e:
            raise ValueError(f"Error parsing XML payload: {e!r}")

    else:
        try:
            dataset_dict = json.loads(dataset_data) if isinstance(dataset_data, str) else dataset_data
        except Exception as e:
            raise ValueError(
                f"Error parsing JSON payload (XML is{' not' if not accept_xml_payload else ''}) accepted: {e!r}")

    investigation_name: str = dataset_dict.get("investigation")
    if not investigation_name:
        raise ValueError("Investigation not found in payload.")

    instrument: str = dataset_dict.get("instrument")
    if not instrument:
        raise ValueError("Instrument not found in payload.")

    dataset_name: str = dataset_dict.get("name")
    if not dataset_name:
        raise ValueError("Dataset name not found in payload.")

    location: str = dataset_dict.get("location")
    if not location:
        raise ValueError("Dataset location not found in payload.")

    start_date: str = dataset_dict.get("startDate")
    if not start_date:
        raise ValueError("Dataset start date not found in payload.")

    end_date: str = dataset_dict.get("endDate")
    if not end_date:
        raise ValueError("Dataset end date not found in payload.")
