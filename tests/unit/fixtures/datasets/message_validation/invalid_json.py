import pytest


@pytest.fixture()
def json_message_missing_investigation():
    return {
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
def json_message_missing_instrument():
    return {
        "investigation": "2022097034",
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
def json_message_missing_name():
    return {
        "investigation": "2022097034",
        "instrument": "bl13",
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
def json_message_missing_location():
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
def json_message_missing_start_date():
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
def json_message_missing_end_date():
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
def json_message_missing_param_value():
    return {
        "investigation": "2022097034",
        "instrument": "bl13",
        "name": "mxau_241222",
        "parameters": [
            {
                "name": "parameter_1",
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
def json_message_missing_param_name():
    return {
        "investigation": "2022097034",
        "instrument": "bl13",
        "name": "mxau_241222",
        "parameters": [
            {
                "name": "",
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
def json_message_empty_datafile_location():
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
                "location": "",
                "size": 942040
            }
        ]
    }

@pytest.fixture()
def json_message_empty_sample_name():
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
            "name": ""
        },
        "datafiles": [
            {
                "location": "/data/bl13/2022097034/mxau_241222.nxs",
                "size": 942040
            }
        ]
    }

@pytest.fixture()
def json_message_too_many_datafiles():
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
            "name": "test"
        },
        "datafiles": [
            {
                "location": "/data/bl13/2022097034/mxau_241222.nxs",
                "size": 942040
            } for _ in range(30002)
        ]
    }

@pytest.fixture()
def json_message_duplicate_parameters():
    return {
        "investigation": "2022097034",
        "instrument": "bl13",
        "name": "mxau_241222",
        "parameters": [
            {
                "name": "parameter_1",
                "value": "872,312"
            },
            {
                "name": "parameter_1",
                "value": "872,312"
            }
        ],
        "location": "/data/bl13/",
        "start_date": "2019-08-08T15:57:45.920+02:00",
        "end_date": "2021-05-30T15:19:08.422+02:00",
        "sample": {
            "name": "test"
        },
        "datafiles": [
            {
                "location": "/data/bl13/2022097034/mxau_241222.nxs",
                "size": 942040
            }
        ]
    }