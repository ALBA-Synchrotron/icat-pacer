import pytest


@pytest.fixture()
def valid_json_raw_dataset_payload():
    return {
        "investigation": "2022097034",
        "instrument": "bl13",
        "name": "mxau_241222",
        "parameters": [
            {
                "name": "parameter_1",
                "value": "872,312"
            }
        ],
        "location": "/data/bl13/",
        "start_date": "2019-08-08T15:57:45.920+02:00",
        "end_date": "2021-05-30T15:19:08.422+02:00",
        "sample": {
            "name": "SAMPLE 1"
        },
        "datafiles": [
            {
                "location": "/data/bl13/2022097034/mxau_241222.nxs",
                "size": 942040
            }
        ]
    }


@pytest.fixture()
def valid_json_processed_dataset_payload():
    return {
        "investigation": "2022097034",
        "instrument": "bl13",
        "name": "mxau_241222",
        "parameters": [
            {
                "name": "input_datasets",
                "value": "872,312"
            }
        ],
        "location": "/data/bl13/",
        "start_date": "2019-08-08T15:57:45.920+02:00",
        "end_date": "2021-05-30T15:19:08.422+02:00",
        "sample": {
            "name": "SAMPLE 1"
        },
        "datafiles": [
            {
                "location": "/data/bl13/2022097034/mxau_241222.nxs",
                "size": 942040
            }
        ]
    }


@pytest.fixture()
def valid_json_raw_dataset_investigation_id_payload():
    return {
        "investigation_id": "19765",
        "instrument": "bl13",
        "name": "mxau_241222",
        "parameters": [
            {
                "name": "parameter_1",
                "value": "872,312"
            }
        ],
        "location": "/data/bl13/",
        "start_date": "2019-08-08T15:57:45.920+02:00",
        "end_date": "2021-05-30T15:19:08.422+02:00",
        "sample": {
            "name": "SAMPLE 1"
        },
        "datafiles": [
            {
                "location": "/data/bl13/2022097034/mxau_241222.nxs",
                "size": 942040
            }
        ]
    }


@pytest.fixture()
def no_datafiles_json_raw_dataset_payload():
    return {
        "investigation": "2022097034",
        "instrument": "bl13",
        "name": "mxau_241222",
        "parameters": [
            {
                "name": "parameter_1",
                "value": "872,312"
            }
        ],
        "location": "/data/bl13/",
        "start_date": "2019-08-08T15:57:45.920+02:00",
        "end_date": "2021-05-30T15:19:08.422+02:00",
        "sample": {
            "name": "SAMPLE 1"
        },
        "datafiles": [
        ]
    }


@pytest.fixture()
def valid_json_raw_dataset_sketchy_datafile_location_payload():
    return {
        "investigation_id": "19765",
        "instrument": "bl13",
        "name": "mxau_241222",
        "parameters": [
            {
                "name": "parameter_1",
                "value": "872,312"
            }
        ],
        "location": "/data/bl13/",
        "start_date": "2019-08-08T15:57:45.920+02:00",
        "end_date": "2021-05-30T15:19:08.422+02:00",
        "sample": {
            "name": "SAMPLE 1"
        },
        "datafiles": [
            {
                "location": "/data/bl13/2022097034/mxau_241222.nxs",
                "size": 942040
            },
            {
                "location": "/etc/passwd",
                "size": 942040
            },
            {
                "location": "/data/../etc/passwd",
                "size": 942040
            }
        ]
    }


@pytest.fixture()
def valid_json_raw_dataset_sketchy_location_payload():
    return {
        "investigation_id": "19765",
        "instrument": "bl13",
        "name": "mxau_241222",
        "parameters": [
            {
                "name": "parameter_1",
                "value": "872,312"
            }
        ],
        "location": "/tmp/../etc/",
        "start_date": "2019-08-08T15:57:45.920+02:00",
        "end_date": "2021-05-30T15:19:08.422+02:00",
        "sample": {
            "name": "SAMPLE 1"
        },
        "datafiles": [
        ]
    }

