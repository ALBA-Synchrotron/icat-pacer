from __future__ import absolute_import, unicode_literals

import logging
from contextlib import suppress

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from exceptions.dataset import DatasetIndexingError
from helpers.integrations.icat.extended_client import ICATClient
from helpers.models.dataset import DatasetIndexingContext
from helpers.utils.base_tasks import BaseTasks


class DatasetsIndexingTasks(BaseTasks):

    def __init__(self, logger: logging.Logger = None):
        super().__init__(logger)

    def index_dataset_elasticsearch(self, icat_client: ICATClient, elastic_client: Elasticsearch,
                                    index_ctx: DatasetIndexingContext, *_args,
                                    **kwargs) -> None:
        try:
            dataset_doc: dict = self.create_dataset_document(icat_client, index_ctx.dataset_id, *_args, **kwargs)

        except Exception as e:
            self.logger.error(f"Error generating document for dataset id={index_ctx.dataset_id}: {e}")
            raise e

        dataset_doc = {
            **{
                k: v
                for k, v in dataset_doc.items()
                if not isinstance(v, list)
            },
            "_index": index_ctx.index_name,
            "_id": index_ctx.dataset_id,
        }

        try:
            bulk(elastic_client, [dataset_doc])
        except Exception as e:
            self.logger.error(f"Error indexing dataset id={index_ctx.dataset_id}: {e}")
            raise DatasetIndexingError(f"Error indexing dataset id={index_ctx.dataset_id}: {e.errors}")
        self.logger.info(f"Indexed dataset id={index_ctx.dataset_id}")

    def create_dataset_document(self, icat_client: ICATClient, dataset_id: int, *_args,
                                **kwargs) -> dict:

        dataset = icat_client.search("Dataset", conditions={"id__eq": dataset_id})

        dataset_investigation = dataset.investigation
        dataset_sample = dataset.sample
        dataset_instrument = dataset_investigation.investigationInstruments[
            0].instrument if dataset_investigation.investigationInstruments else None

        if not "investigation" in kwargs.get("shared_obj_identifiers", {}):
            kwargs.get("shared_obj_identifiers", {})["visit_id"] = dataset_investigation.visitId
            kwargs.get("shared_obj_identifiers", {})["investigation"] = dataset_investigation.name

        self.logger.info(
            f"Building dataset document for dataset id={dataset_id}, inv={dataset_investigation.name}")

        dataset_doc: dict = {
            "id": dataset.id,
            "name": dataset.name,
            "location": dataset.location,
            "type": dataset.type.name,
            "sampleName": dataset_sample.name,
            "sampleId": dataset_sample.id,
            "startDate": dataset.startDate.isoformat() if dataset.startDate else None,
            "endDate": dataset.endDate.isoformat() if dataset.endDate else None,
            "investigationId": dataset_investigation.id,
            "investigationName": dataset_investigation.name,
            "investigationSummary": dataset_investigation.summary,
            "investigationTitle": dataset_investigation.title,
            "investigationVisitId": dataset_investigation.visitId,
            "releaseDate": dataset_investigation.releaseDate.isoformat() if dataset_investigation.releaseDate else None,
            "investigationDOI": dataset_investigation.doi,
            "estype": "dataset",
            "parametersCount": len(dataset.parameters),
            "definition": "undefined"
        }

        if dataset_instrument:
            dataset_doc["instrumentName"] = dataset_instrument.name.replace("-", "")
            dataset_doc["instrumentId"] = dataset_instrument.id

        composed_params: dict = {}

        for dataset_param in dataset.parameters:

            param_value = dataset_param.stringValue if dataset_param.stringValue else dataset_param.numericValue

            if not param_value:
                continue

            dataset_param_type_name: str = dataset_param.type.name
            es_dataset_param_type_name: str = dataset_param_type_name.replace("__", "")
            dataset_doc[es_dataset_param_type_name] = param_value

            match dataset_param_type_name:
                case "scanType":
                    dataset_doc["definition"] = param_value
                case "InstrumentMonochromator_energy" | "InstrumentMonochromator_wavelength" | "InstrumentSource_current":
                    with suppress(ValueError):
                        dataset_doc[es_dataset_param_type_name] = float(param_value)
                case "volume" | "fileCount" | "_metadataSize":
                    with suppress(Exception):
                        dataset_doc[es_dataset_param_type_name] = int(param_value)

            if dataset_param_type_name.endswith(("_name", "_value")):
                composed_key, param_kind = dataset_param_type_name.rsplit("_", 1)
                if composed_key not in composed_params:
                    composed_params[composed_key] = {}
                composed_params[composed_key][param_kind] = param_value

        for composed_key, dataset_composed_param in composed_params.items():
            names: list = dataset_composed_param.get("name", "").split(" ")
            values: list = dataset_composed_param.get("value", "").split(" ")
            merged: list = []

            if len(names) != len(values):
                self.logger.warning(
                    f"Skipping composed dataset parameter {composed_key} for dataset id={dataset_id}, inv={dataset_investigation.name} due to mismatched number of names and values")
                continue

            for name, value in zip(names, values):
                try:
                    float_val: float = float(value)
                except ValueError:
                    float_val: float = float("nan")

                merged.append({"name": name, "numericValue": float_val, "stringValue": value})

            if merged:
                dataset_doc[composed_key] = merged

        compact_search_values: list = [dataset_investigation.visitId, dataset_investigation.summary,
                                       dataset_investigation.name,
                                       dataset_doc.get("InstrumentMonochromatorCrystal_reflection", ""),
                                       dataset_doc.get("InstrumentMonochromatorCrystal_type", ""),
                                       dataset_doc.get("InstrumentMonochromatorCrystal_usage", ""),
                                       dataset_doc.get("definition", ""),
                                       dataset.name, dataset_sample.name]

        dataset_doc = {
            **dataset_doc,
            "escompactsearch": " ".join(s for s in compact_search_values if s is not None),
        }

        dataset_doc["_metadataSize"] = len(dataset_doc)

        self.logger.info(
            f"Built dataset document for dataset id={dataset_id}, inv={dataset_investigation.name}")
        return dataset_doc
