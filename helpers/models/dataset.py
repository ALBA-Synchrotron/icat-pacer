from dataclasses import dataclass

from pydantic import BaseModel

from exceptions.dataset import DatasetValidationError, DatasetParameterValidationError, DatasetDatafileValidationError, \
    DatasetSampleValidationError



class DatasetSampleContext(BaseModel):
    name: str
    type: str


@dataclass
class DatasetDatafileContext:
    location: str

    def __post_init__(self):
        if not self.location:
            raise DatasetDatafileValidationError("Datafile location cannot be empty")


@dataclass
class DatasetParameterContext:
    name: str
    value: str

    def __post_init__(self):
        if self.name is None or not self.name:
            raise DatasetParameterValidationError("Dataset parameter name cannot be empty")
        if self.value is None:
            raise DatasetParameterValidationError("Dataset parameter value cannot be empty")


@dataclass
class DatasetContext:
    investigation: str
    investigation_id: int
    instrument: str
    name: str
    parameters: list[DatasetParameterContext]
    location: str
    start_date: str
    end_date: str
    sample: DatasetSampleContext
    datafiles: list[DatasetDatafileContext]
    type: str = ""

    def __post_init__(self):
        if not self.investigation and not self.investigation_id:
            raise DatasetValidationError(f"Investigation name nor id not found in payload")

        if not self.instrument:
            raise DatasetValidationError(f"Instrument not found in payload")

        if not self.name:
            raise DatasetValidationError(f"Name not found in payload")

        if not self.location:
            raise DatasetValidationError(f"Location not found in payload")

        if not self.start_date:
            raise DatasetValidationError(f"Start date not found in payload")

        if not self.end_date:
            raise DatasetValidationError(f"End date not found in payload")
