from dataclasses import dataclass


@dataclass
class DatasetSampleContext:
    name: str
    type: str

    def __post_init__(self):
        if not self.name:
            raise ValueError("Sample name cannot be empty")

@dataclass
class DatasetDatafileContext:
    location: str

    def __post_init__(self):
        if not self.location:
            raise ValueError("Datafile location cannot be empty")


@dataclass
class DatasetParameterContext:
    name: str
    value: str

    def __post_init__(self):
        if self.name is None:
            raise ValueError("Dataset parameter name cannot be empty")
        if self.value is None:
            raise ValueError("Dataset parameter value cannot be empty")


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
            raise ValueError(f"Investigation name nor id not found in payload")

        if not self.instrument:
            raise ValueError(f"Instrument not found in payload")

        if not self.name:
            raise ValueError(f"Name not found in payload")

        if not self.location:
            raise ValueError(f"Location not found in payload")

        if not self.start_date:
            raise ValueError(f"Start date not found in payload")

        if not self.end_date:
            raise ValueError(f"End date not found in payload")

        if not self.datafiles:
            raise ValueError(f"Data files not found in payload")
