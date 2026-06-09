import os
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, model_validator, field_validator, Field

import globals_var
from exceptions.dataset import DatasetValidationError, DatasetDatafileLimitExceeded
from helpers.static_settings import INPUT_DATASET_PARAMETER_NAME, PROCESSED_DATASET_TYPE_NAME, RAW_DATASET_TYPE_NAME


class DatasetSampleContext(BaseModel):
    name: str = Field(min_length=1)
    type: str = ""

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        ingestion_settings: dict = globals_var.ingestion_settings.get("dataset", {})
        if not v and ingestion_settings.get("mandatorySampleType"):
            raise DatasetValidationError("Sample type is mandatory but not provided")
        return v


class DatasetDatafileContext(BaseModel):
    location: str = Field(min_length=1)


class DatasetParameterContext(BaseModel):
    name: str = Field(min_length=1)
    value: str = Field(min_length=1)


@dataclass
class DatasetContext(BaseModel):
    sample: DatasetSampleContext
    investigation: str
    instrument: str = Field(min_length=1)
    name: str = Field(min_length=1)
    location: str = Field(min_length=1)
    start_date: str = Field(min_length=1)
    end_date: str = Field(min_length=1)
    parameters: list[DatasetParameterContext] = Field(min_length=0)
    datafiles: list[DatasetDatafileContext] = Field(min_length=0)
    type: str = ""
    investigation_id: int = 0

    @model_validator(mode="after")
    def investigation_name_validator(self):
        if self.investigation == '' and  self.investigation_id == 0:
            raise DatasetValidationError("Investigation name nor id not found in payload")
        return self

    @model_validator(mode="after")
    def set_dataset_type(self):
        has_input_param: bool = INPUT_DATASET_PARAMETER_NAME in [i.name for i in self.parameters]
        if has_input_param:
            self.type = PROCESSED_DATASET_TYPE_NAME
        else:
            self.type = RAW_DATASET_TYPE_NAME
        return self

    @model_validator(mode="after")
    def dynamic_validations(self, location=None):
        ingestion_settings: dict = globals_var.ingestion_settings.get("dataset", {})
        if not ingestion_settings.get("automaticDatasetLocationIndex") and not self.datafiles:
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

            if not all(is_df_location_in_allowed_roots(i.location) for i in self.datafiles):
                raise DatasetValidationError(
                    f"Datafile location(s) outside of allowed root location(s), valid root are: {",".join(allowed_root_locations)}")

            if not is_df_location_in_allowed_roots(self.location):
                raise DatasetValidationError(
                    f"Dataset location outside of allowed root location(s), valid root are: {",".join(allowed_root_locations)}")

        # Avoid double file existence check if strict check / resolution has been done before.
        if ingestion_settings.get("mandatoryPathsExistence") and not ingestion_settings.get(
                "checkAllowedLocationPaths"):
            if not os.path.exists(location):
                raise DatasetValidationError(f"Dataset root location does not exist: {location}")

            for datafile in self.datafiles:
                if not os.path.exists(datafile.location):
                    raise DatasetValidationError(
                        f"Dataset's datafile root location does not exist: {datafile.location}")

        if len(self.datafiles) > ingestion_settings.get("maxDatafilesPerDataset", 30000):
            raise DatasetDatafileLimitExceeded(
                f"Too many datafiles ({len(self.datafiles)}) in dataset, ingestion rejected due to limit exceeded")

        param_names = [i.name for i in self.parameters]
        if len(param_names) != len(set(param_names)):
            raise DatasetValidationError(f"Duplicate parameter names found in dataset: {param_names}")

        return self
