# ICAT User roles
ICAT_USER_ROLE_PRINCIPAL_INVESTIGATOR: str = "Principal investigator"
ICAT_USER_ROLE_PROPOSER: str = "Proposal scientist"
ICAT_USER_ROLE_PARTICIPANT: str = "Participant"
ICAT_USER_ROLE_LOCAL_CONTACT: str = "Local contact"

# Datacite proposal user roles
DATACITE_CONTRIBUTOR_PROJECT_MANAGER: str = "ProjectManager"
DATACITE_CONTRIBUTOR_PROJECT_MEMBER: str = "ProjectMember"
DATACITE_CONTRIBUTOR_DATA_COLLECTOR: str = "DataCollector"

# Raw and processed dataset relations
INPUT_DATASET_PARAMETER_NAME: str = "input_datasets"
RAW_DATASET_TYPE_NAME: str = "acquisition"
PROCESSED_DATASET_TYPE_NAME: str = "processed"
REPROCESSED_DATASET_TYPE_NAME: str = "reprocessed"

# Dataset statistics
DATASET_FILE_COUNT_PARAMETER: str = "__fileCount"
DATASET_VOLUME_PARAMETER: str = "__volume"
DATASET_ELAPSE_TIME_PARAMETER: str = "__elapsedTime"

# Investigation statistics
INVESTIGATION_DATASET_COUNT_PARAMETER: str = "__datasetCount"
INVESTIGATION_ACQUISITION_DATASET_COUNT_PARAMETER: str = "__acquisitionDatasetCount"
INVESTIGATION_PROCESSED_DATASET_COUNT_PARAMETER: str = "__processedDatasetCount"
INVESTIGATION_SAMPLE_COUNT_PARAMETER: str = "__sampleCount"
INVESTIGATION_VOLUME_PARAMETER: str = "__volume"
INVESTIGATION_ACQUISITION_VOLUME_PARAMETER: str = "__acquisitionVolume"
INVESTIGATION_PROCESSED_VOLUME_PARAMETER: str = "__processedVolume"
INVESTIGATION_ELAPSE_TIME_PARAMETER: str = "__elapsedTime"
INVESTIGATION_FILE_COUNT_PARAMETER: str = "__fileCount"
INVESTIGATION_ACQUISITION_FILE_COUNT_PARAMETER: str = "__acquisitionFileCount"
INVESTIGATION_PROCESSED_FILE_COUNT_PARAMETER: str = "__processedFileCount"

# Sample statistics
SAMPLE_DATASET_COUNT_PARAMETER: str = "__datasetCount"
SAMPLE_ACQUISITION_DATASET_COUNT_PARAMETER: str = "__acquisitionDatasetCount"
SAMPLE_PROCESSED_DATASET_COUNT_PARAMETER: str = "__processedDatasetCount"
SAMPLE_FILE_COUNT_PARAMETER: str = "__fileCount"
SAMPLE_ACQUISITION_FILE_COUNT_PARAMETER: str = "__acquisitionFileCount"
SAMPLE_PROCESSED_FILE_COUNT_PARAMETER: str = "__processedFileCount"
SAMPLE_VOLUME_PARAMETER: str = "__volume"
SAMPLE_ACQUISITION_VOLUME_PARAMETER: str = "__acquisitionVolume"
SAMPLE_PROCESSED_VOLUME_PARAMETER: str = "__processedVolume"

# Internal dataset parameters names
DATASET_NAME_PARAMETER: str = "datasetName"
INPUT_DATASET_IDS_PARAMETER_NAME: str = "input_datasetIds"
OUTPUT_DATASET_IDS_PARAMETER_NAME: str = "output_datasetIds"
OUTPUT_DATASET_NAMES_PARAMETER_NAME: str = "output_datasetNames"
OUTPUT_DATASET_DATASETS_PARAMETER_NAME: str = "output_datasets"
FULL_INPUT_DATASET_IDS_PARAM: str = "__full_input_datasetIds"
FULL_OUTPUT_DATASET_IDS_PARAM: str = "__full_output_datasetIds"
FULL_INPUT_DATASET_NAMES_PARAM: str = "__full_input_datasetNames"
FULL_OUTPUT_DATASET_NAMES_PARAM: str = "__full_output_datasetNames"

PARAMETER_STRING_VALUE_MAX_LENGTH: int = 4000

LRU_CACHE_MAX: int = 1024