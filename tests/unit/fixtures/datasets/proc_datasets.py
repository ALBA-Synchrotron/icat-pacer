import pytest


@pytest.fixture
def json_proc_dataset(ingestion_files_for_testing, test_investigation, raw_dataset):
    dataset_location, created_files = ingestion_files_for_testing
    return {
        "investigation": test_investigation.name,
        "instrument": test_investigation.investigationInstruments[0].instrument.name,
        "name": "mxau_241222_json",
        "parameters": [
            {
                "name": "input_datasets",
                "value": f"{raw_dataset.id}"
            },
            {
                "name": "Process_sequence_index",
                "value": "1"
            },
            {
                "name": "parameter_type_1",
                "value": "yes"
            }
        ],
        "location": str(dataset_location),
        "start_date": "2025-09-23T10:00:45.920+02:00",
        "end_date": "2025-09-23T10:19:08.422+02:00",
        "sample": {
            "name": "SAMPLE 1"
        },
        "datafiles": [
            {
                "location": str(i),
                "size": created_files[i]
            } for i in created_files
        ]
    }


@pytest.fixture()
def xml_proc_dataset(ingestion_files_for_testing, test_investigation, raw_dataset):
    dataset_location, created_files = ingestion_files_for_testing
    datafile_elements = "\n".join(
        f"""
        <datafile>
            <location>{str(i)}</location>
            <size>{created_files[i]}</size>
        </datafile>
        """ for i in created_files
    )
    return f"""
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <dataset>
            <investigation>{test_investigation.name}</investigation>
            <instrument>{test_investigation.investigationInstruments[0].instrument.name}</instrument>
            <name>mxau_241222_xml</name>
            <parameter>
                    <name>input_datasets</name>
                    <value>{raw_dataset.id}</value>
            </parameter>
            <parameter>
                    <name>Process_sequence_index</name>
                    <value>1</value>
            </parameter>
            <parameter>
                    <name>parameter_type_1</name>
                    <value>yes</value>
            </parameter>
            <location>{str(dataset_location)}</location>
            <startDate>2025-09-23T10:00:45.920+02:00</startDate>
            <endDate>2025-09-23T10:19:08.422+02:00</endDate>
            <sample> 
                <name>SAMPLE 1</name>
            </sample>
            {datafile_elements}
        </dataset>
        """