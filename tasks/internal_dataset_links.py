from __future__ import absolute_import, unicode_literals

import logging

from icat.entity import Entity

from exceptions.dataset import DatasetValidationError, DatasetNotFound
from helpers.integrations.icat.extended_client import ICATClient
from helpers.static_settings import INPUT_DATASET_IDS_PARAMETER_NAME, FULL_INPUT_DATASET_IDS_PARAMETER_NAME, \
    OUTPUT_DATASET_IDS_PARAMETER_NAME, FULL_OUTPUT_DATASET_IDS_PARAMETER_NAME, DATASET_NAME_PARAMETER, \
    FULL_INPUT_DATASET_NAMES_PARAMETER_NAME, FULL_OUTPUT_DATASET_NAMES_PARAMETER_NAME
from helpers.utils.base_tasks import BaseTasks
from helpers.utils.dataset import get_dataset_parameter, set_dataset_parameter
from helpers.utils.icat_rollback_proxy import ICATRollbackContext


class InternalDatasetLinksTasks(BaseTasks):

    def __init__(self, logger: logging.Logger = None):
        super().__init__(logger)

    @classmethod
    def __get_dataset_name(cls, dataset: Entity, dataset_map: dict) -> str:
        if dataset.id in dataset_map and DATASET_NAME_PARAMETER in dataset_map[dataset.id]:
            return dataset_map[dataset.id][DATASET_NAME_PARAMETER]

        dataset_name_param = next(
            (i for i in dataset.parameters if i.type.name == DATASET_NAME_PARAMETER),
            None
        )

        if not dataset_name_param:
            dataset_name = dataset.name
        else:
            dataset_name = dataset_name_param.stringValue

        return dataset_name

    def __get_all_dataset_links_ids(self, icat_client: ICATClient, dataset_id: int, link_param_name: str,
                                    full_link_param_name: str, dataset_map: dict) -> tuple[list, dict]:

        if dataset_id in dataset_map and link_param_name in dataset_map[dataset_id]:
            return dataset_map[dataset_id][link_param_name], dataset_map

        dataset = icat_client.search(
            "Dataset",
            conditions={"id__eq": dataset_id},
            flatten_single=True
        )

        dataset_link_ids_param = next(
            (i for i in dataset.parameters if i.type.name == link_param_name),
            None
        )
        dataset_link_ids = (
            dataset_link_ids_param.stringValue.split(" ")
            if dataset_link_ids_param
            else []
        )
        dataset_link_ids = [int(i) for i in dataset_link_ids]

        dataset_name = self.__get_dataset_name(dataset, dataset_map)

        updated_dataset_map = {**dataset_map}

        current_dataset_data = updated_dataset_map.get(dataset_id, {}).copy()
        current_dataset_data[DATASET_NAME_PARAMETER] = dataset_name

        for link_id in {int(i) for i in dataset_link_ids}:
            new_ids, updated_dataset_map = self.__get_all_dataset_links_ids(
                icat_client,
                link_id,
                link_param_name,
                full_link_param_name,
                updated_dataset_map
            )
            dataset_link_ids.extend(i for i in new_ids if i not in dataset_link_ids)

        current_dataset_data[full_link_param_name] = dataset_link_ids
        updated_dataset_map[dataset_id] = current_dataset_data

        return dataset_link_ids, updated_dataset_map

    def __build_dataset_links_map(self, icat_client: ICATClient, dataset_id: int) -> dict:
        dataset_map = {}

        parameters = [
            (INPUT_DATASET_IDS_PARAMETER_NAME, FULL_INPUT_DATASET_IDS_PARAMETER_NAME),
            (OUTPUT_DATASET_IDS_PARAMETER_NAME, FULL_OUTPUT_DATASET_IDS_PARAMETER_NAME)
        ]

        self.logger.info(f"Retrieve all input and output datasets for dataset id={dataset_id}")
        for parameter_name, full_parameter_name in parameters:
            _, dataset_map = self.__get_all_dataset_links_ids(
                icat_client,
                dataset_id,
                parameter_name,
                full_parameter_name,
                dataset_map
            )

        self.logger.info(f"Retrieve all input datasetsIds for all children of dataset id={dataset_id}")
        input_ids: list = dataset_map.get(dataset_id, {}).get(FULL_INPUT_DATASET_IDS_PARAMETER_NAME, [])
        for link_id in input_ids:
            _, dataset_map = self.__get_all_dataset_links_ids(
                icat_client,
                link_id,
                OUTPUT_DATASET_IDS_PARAMETER_NAME,
                FULL_OUTPUT_DATASET_IDS_PARAMETER_NAME,
                dataset_map
            )

        self.logger.info(f"Retrieve all output datasetsIds for all parents of dataset id={dataset_id}")
        output_ids: list = dataset_map.get(dataset_id, {}).get(FULL_OUTPUT_DATASET_IDS_PARAMETER_NAME, [])
        for link_id in output_ids:
            _, dataset_map = self.__get_all_dataset_links_ids(
                icat_client,
                link_id,
                INPUT_DATASET_IDS_PARAMETER_NAME,
                FULL_INPUT_DATASET_IDS_PARAMETER_NAME,
                dataset_map
            )

        self.logger.info(
            f"Retrieve all input and output dataset names for all datasets linked to dataset id={dataset_id}")
        for map_id in dataset_map:
            input_ids = dataset_map[map_id].get(FULL_INPUT_DATASET_IDS_PARAMETER_NAME, [])
            input_datasets = icat_client.search("Dataset", conditions={"id__in": input_ids}, flatten_single=False)

            output_ids = dataset_map[map_id].get(FULL_OUTPUT_DATASET_IDS_PARAMETER_NAME, [])
            output_datasets = icat_client.search("Dataset", conditions={"id__in": output_ids}, flatten_single=False)

            dataset_map[map_id][FULL_INPUT_DATASET_NAMES_PARAMETER_NAME] = [
                self.__get_dataset_name(dataset, dataset_map)
                for dataset in input_datasets]
            dataset_map[map_id][FULL_OUTPUT_DATASET_NAMES_PARAMETER_NAME] = [
                self.__get_dataset_name(dataset, dataset_map)
                for dataset in output_datasets]

        return dataset_map

    def build_dataset_full_links_information(self, icat_client: ICATClient, dataset_id: int, *_args, **kwargs) -> None:
        if not dataset_id:
            raise DatasetValidationError("Dataset ID not received")

        parameters = [FULL_INPUT_DATASET_IDS_PARAMETER_NAME, FULL_OUTPUT_DATASET_IDS_PARAMETER_NAME,
                      FULL_INPUT_DATASET_NAMES_PARAMETER_NAME, FULL_OUTPUT_DATASET_NAMES_PARAMETER_NAME]

        with ICATRollbackContext(icat_client, self.logger) as rb:
            try:
                self.logger.info(
                    f"Start build of full input and output dataset links information for dataset id={dataset_id}")
                rb.dataset = icat_client.search("Dataset", conditions={"id__eq": dataset_id}, flatten_single=True)

                if not rb.dataset:
                    raise DatasetNotFound("Dataset not found")

                if not "visit_id" in kwargs["shared_obj_identifiers"]:
                    kwargs["shared_obj_identifiers"]["visit_id"] = rb.dataset.investigation.visitId

                datasets_map = self.__build_dataset_links_map(icat_client, dataset_id)

                for index, map_dataset_id in enumerate(datasets_map):
                    dataset_info: dict = datasets_map[map_dataset_id]

                    for param in parameters:
                        if param not in dataset_info:
                            dataset_info[param] = []
                        param_value: str = " ".join(str(i) for i in dataset_info[param])

                        if param_value:
                            dataset_param = get_dataset_parameter(icat_client, param, dataset_id=map_dataset_id)
                            setattr(rb, f"{index}_dataset_{param}", dataset_param)

                            dataset_param = set_dataset_parameter(dataset_param, param_value)
                            setattr(rb, f"{index}_dataset_{param}", dataset_param)

                self.logger.info(
                    f"Finished completion of full input and output information for dataset id={dataset_id} ")
            except Exception as e:
                rb.rollback_all(force_delete=True)

                error_msg: str = f"Error: {e}"
                self.logger.error(error_msg)
                raise e
