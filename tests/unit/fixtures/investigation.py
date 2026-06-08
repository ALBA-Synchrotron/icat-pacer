import pytest


@pytest.fixture()
def investigation_non_existent_user():
    return {
        "name": "2025079976",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "title": "test_title",
        "summary": "test_summary",
        "instrument": {
            "name": "BL13 - XALOC",
            "code": "BL13"
        },
        "type": "MX",
        "user_list": [
            {"username": "testuser", "email": "test_email@<<>>.com", "role": "Principal investigator"},
        ],
        "visit_count": 1,
        "is_reimbursed": True,
        "icat_visit_id": "uo_8623",
        "visa_visit_id": 1008623,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }

@pytest.fixture()
def investigation_payload_empty_name():
    return {
        "name": "",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "title": "test_title",
        "summary": "test_summary",
        "instrument": {
            "name": "BL13 - XALOC",
            "code": "BL13"
        },
        "type": "MX",
        "user_list": [
            {"username": "testuser", "email": "test_email@<<>>.com", "role": "Principal investigator"},
            {"username": "testuser", "email": "test_email1@<<>>.com", "role": "Local contact"}
        ],
        "visit_count": 1,
        "is_reimbursed": True,
        "icat_visit_id": "uo_8623",
        "visa_visit_id": 1008623,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }

@pytest.fixture()
def investigation_payload_empty_facility():
    return {
        "name": "2025079999",
        "facility": None,
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "title": "test_title",
        "summary": "test_summary",
        "instrument": {
            "name": "BL13 - XALOC",
            "code": "BL13"
        },
        "type": "MX",
        "user_list": [
            {"username": "testuser", "email": "test_email@<<>>.com", "role": "Principal investigator"},
            {"username": "testuser", "email": "test_email1@<<>>.com", "role": "Local contact"}
        ],
        "visit_count": 1,
        "is_reimbursed": True,
        "icat_visit_id": "uo_8623",
        "visa_visit_id": 1008623,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }

@pytest.fixture()
def investigation_payload_empty_start_date():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": None,
        "end_date": "2025-07-02T00:00:00Z",
        "title": "test_title",
        "summary": "test_summary",
        "instrument": {
            "name": "BL13 - XALOC",
            "code": "BL13"
        },
        "type": "MX",
        "user_list": [
            {"username": "testuser", "email": "test_email@<<>>.com", "role": "Principal investigator"},
            {"username": "testuser", "email": "test_email1@<<>>.com", "role": "Local contact"}
        ],
        "visit_count": 1,
        "is_reimbursed": True,
        "icat_visit_id": "uo_8623",
        "visa_visit_id": 1008623,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }

@pytest.fixture()
def investigation_payload_empty_end_date():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": None,
        "title": "test_title",
        "summary": "test_summary",
        "instrument": {
            "name": "BL13 - XALOC",
            "code": "BL13"
        },
        "type": "MX",
        "user_list": [
            {"username": "testuser", "email": "test_email@<<>>.com", "role": "Principal investigator"},
            {"username": "testuser", "email": "test_email1@<<>>.com", "role": "Local contact"}
        ],
        "visit_count": 1,
        "is_reimbursed": True,
        "icat_visit_id": "uo_8623",
        "visa_visit_id": 1008623,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }

@pytest.fixture()
def investigation_payload_empty_title():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "title": "",
        "summary": "test_summary",
        "instrument": {
            "name": "BL13 - XALOC",
            "code": "BL13"
        },
        "type": "MX",
        "user_list": [
            {"username": "testuser", "email": "test_email@<<>>.com", "role": "Principal investigator"},
            {"username": "testuser", "email": "test_email1@<<>>.com", "role": "Local contact"}
        ],
        "visit_count": 1,
        "is_reimbursed": True,
        "icat_visit_id": "uo_8623",
        "visa_visit_id": 1008623,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }


@pytest.fixture()
def investigation_payload_empty_summary():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "title": "test_title",
        "summary": "",
        "instrument": {
            "name": "BL13 - XALOC",
            "code": "BL13"
        },
        "type": "MX",
        "user_list": [
            {"username": "testuser", "email": "test_email@<<>>.com", "role": "Principal investigator"},
            {"username": "testuser", "email": "test_email1@<<>>.com", "role": "Local contact"}
        ],
        "visit_count": 1,
        "is_reimbursed": True,
        "icat_visit_id": "uo_8623",
        "visa_visit_id": 1008623,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }


@pytest.fixture()
def investigation_payload_empty_instrument():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "title": "test_title",
        "summary": "test_summary",
        "instrument": None,
        "type": "MX",
        "user_list": [
            {"username": "testuser", "email": "test_email@<<>>.com", "role": "Principal investigator"},
            {"username": "testuser", "email": "test_email1@<<>>.com", "role": "Local contact"}
        ],
        "visit_count": 1,
        "is_reimbursed": True,
        "icat_visit_id": "uo_8623",
        "visa_visit_id": 1008623,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }


@pytest.fixture()
def investigation_payload_empty_type():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "title": "test_title",
        "summary": "test_summary",
        "instrument": {
            "name": "BL13 - XALOC",
            "code": "BL13"
        },
        "type": "",
        "user_list": [
            {"username": "testuser", "email": "test_email@<<>>.com", "role": "Principal investigator"},
            {"username": "testuser", "email": "test_email1@<<>>.com", "role": "Local contact"}
        ],
        "visit_count": 1,
        "is_reimbursed": True,
        "icat_visit_id": "uo_8623",
        "visa_visit_id": 1008623,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }


@pytest.fixture()
def investigation_payload_invalid_missing_username():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "title": "test_title",
        "summary": "test_summary",
        "instrument": {
            "name": "BL13 - XALOC",
            "code": "BL13"
        },
        "type": "MX",
        "user_list": [
            {"username": "", "email": "test_email@<<>>.com", "role": "Principal investigator"},
            {"username": "testuser", "email": "test_email1@<<>>.com", "role": "Local contact"}
        ],
        "visit_count": 1,
        "is_reimbursed": True,
        "icat_visit_id": "uo_8623",
        "visa_visit_id": 1008623,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }

@pytest.fixture()
def investigation_payload_invalid_missing_email():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "title": "test_title",
        "summary": "test_summary",
        "instrument": {
            "name": "BL13 - XALOC",
            "code": "BL13"
        },
        "type": "MX",
        "user_list": [
            {"username": "testuser", "email": "", "role": "Principal investigator"},
            {"username": "testuser", "email": "test_email1@<<>>.com", "role": "Local contact"}
        ],
        "visit_count": 1,
        "is_reimbursed": True,
        "icat_visit_id": "uo_8623",
        "visa_visit_id": 1008623,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }

@pytest.fixture()
def investigation_payload_invalid_missing_role():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "title": "test_title",
        "summary": "test_summary",
        "instrument": {
            "name": "BL13 - XALOC",
            "code": "BL13"
        },
        "type": "MX",
        "user_list": [
            {"username": "testuser", "email": "test_email@<<>>.com", "role": "Principal investigator"},
            {"username": "testuser", "email": "test_email1@<<>>.com", "role": ""}
        ],
        "visit_count": 1,
        "is_reimbursed": True,
        "icat_visit_id": "uo_8623",
        "visa_visit_id": 1008623,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }


@pytest.fixture()
def investigation_payload_invalid_missing_instrument_name():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "title": "test_title",
        "summary": "test_summary",
        "instrument": {
            "name": "",
            "code": "BL13"
        },
        "type": "MX",
        "user_list": [
            {"username": "testuser", "email": "test_email@<<>>.com", "role": "Principal investigator"},
            {"username": "testuser", "email": "test_email1@<<>>.com", "role": "Local contact"}
        ],
        "visit_count": 1,
        "is_reimbursed": True,
        "icat_visit_id": "uo_8623",
        "visa_visit_id": 1008623,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }


@pytest.fixture()
def investigation_payload_invalid_missing_instrument_code():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "title": "test_title",
        "summary": "test_summary",
        "instrument": {
            "name": "BL13 - XALOC",
            "code": ""
        },
        "type": "MX",
        "user_list": [
            {"username": "testuser", "email": "test_email@<<>>.com", "role": "Principal investigator"},
            {"username": "testuser", "email": "test_email1@<<>>.com", "role": "Local contact"}
        ],
        "visit_count": 1,
        "is_reimbursed": True,
        "icat_visit_id": "uo_8623",
        "visa_visit_id": 1008623,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }

@pytest.fixture()
def investigation_payload_invalid_missing_icat_visit_id():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "title": "test_title",
        "summary": "test_summary",
        "instrument": {
            "name": "BL13 - XALOC",
            "code": ""
        },
        "type": "MX",
        "user_list": [
            {"username": "testuser", "email": "test_email@<<>>.com", "role": "Principal investigator"},
            {"username": "testuser", "email": "test_email1@<<>>.com", "role": "Local contact"}
        ],
        "visit_count": 1,
        "is_reimbursed": True,
        "icat_visit_id": None,
        "visa_visit_id": 1008623,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }

@pytest.fixture()
def investigation_payload_invalid_missing_visa_visit_id():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "title": "test_title",
        "summary": "test_summary",
        "instrument": {
            "name": "BL13 - XALOC",
            "code": ""
        },
        "type": "MX",
        "user_list": [
            {"username": "testuser", "email": "test_email@<<>>.com", "role": "Principal investigator"},
            {"username": "testuser", "email": "test_email1@<<>>.com", "role": "Local contact"}
        ],
        "visit_count": 1,
        "is_reimbursed": True,
        "icat_visit_id": "uo_8623",
        "visa_visit_id": None,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }

@pytest.fixture()
def investigation_payload_invalid_user_role_invalid():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "title": "test_title",
        "summary": "test_summary",
        "instrument": {
            "name": "BL13 - XALOC",
            "code": ""
        },
        "type": "MX",
        "user_list": [
            {"username": "testuser", "email": "test_email@<<>>.com", "role": "Principal investigator"},
            {"username": "testuser", "email": "test_email1@<<>>.com", "role": "Random fella"}
        ],
        "visit_count": 1,
        "is_reimbursed": True,
        "icat_visit_id": "uo_8623",
        "visa_visit_id": 1234,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }

@pytest.fixture()
def valid_investigation():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "title": "test_title",
        "summary": "test_summary",
        "instrument": {
            "name": "BL13 - XALOC",
            "code": "BL13"
        },
        "type": "MX",
        "user_list": [
            {"username": "auo-test12", "email": "test_email@<<>>.com", "role": "Principal investigator"},
            {"username": "auo-testTest1-ou12", "email": "test_email1@<<>>.com", "role": "Local contact"}
        ],
        "visit_count": 1,
        "is_reimbursed": True,
        "icat_visit_id": "uo_8623",
        "visa_visit_id": 1008623,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }

@pytest.fixture()
def valid_investigation_update():
    return {
        "name": "20250799991122",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "title": "test_title",
        "summary": "test_summary",
        "instrument": {
            "name": "BL13 - XALOC",
            "code": "BL13"
        },
        "type": "MX",
        "user_list": [
            {"username": "auo-test12", "email": "test_email@<<>>.com", "role": "Principal investigator"},
            {"username": "auo-testTest1-ou12", "email": "test_email1@<<>>.com", "role": "Local contact"}
        ],
        "visit_count": 1,
        "is_reimbursed": True,
        "icat_visit_id": "uo_8623",
        "visa_visit_id": 1008623,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }

@pytest.fixture()
def investigation_non_existent_instrument():
    return {
        "name": "2025079900",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "title": "test_title",
        "summary": "test_summary",
        "instrument": {
            "name": "BL9123 - Gandalf",
            "code": "BL9123"
        },
        "type": "MX",
        "user_list": [
            {"username": "testuser", "email": "test_email@<<>>.com", "role": "Principal investigator"},
            {"username": "testuser1", "email": "test_email1@<<>>.com", "role": "Local contact"}
        ],
        "visit_count": 1,
        "is_reimbursed": True,
        "icat_visit_id": "uo_8623",
        "visa_visit_id": 1008623,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }

@pytest.fixture()
def investigation_non_existent_facility():
    return {
        "name": "202507990011",
        "facility": "GOTERAS",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "title": "test_title",
        "summary": "test_summary",
        "instrument": {
            "name": "BL13 - XALOC",
            "code": "BL13"
        },
        "type": "MX",
        "user_list": [
            {"username": "auo-test12", "email": "test_email@<<>>.com", "role": "Principal investigator"},
            {"username": "auo-testTest1-ou12", "email": "test_email1@<<>>.com", "role": "Local contact"}
        ],
        "visit_count": 1,
        "is_reimbursed": True,
        "icat_visit_id": "uo_8623",
        "visa_visit_id": 1008623,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }

@pytest.fixture()
def investigation_non_existent_investigation_type():
    return {
        "name": "2025079918181",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "title": "test_title",
        "summary": "test_summary",
        "instrument": {
            "name": "BL13 - XALOC",
            "code": "BL13"
        },
        "type": "LEL",
        "user_list": [
            {"username": "auo-test12", "email": "test_email@<<>>.com", "role": "Principal investigator"},
            {"username": "auo-testTest1-ou12", "email": "test_email1@<<>>.com", "role": "Local contact"}
        ],
        "visit_count": 1,
        "is_reimbursed": True,
        "icat_visit_id": "uo_8623",
        "visa_visit_id": 1008623,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }

@pytest.fixture(autouse=True, scope="session")
def icat_users(icat_client):
    user = icat_client.new("User")
    user.name = "auo-test12"
    user.email = "test_email@<<>>.com"
    user.create()

    user2 = icat_client.new("User")
    user2.name = "auo-testtest1-ou12"
    user2.email = "test_email@<<>>.com"
    user2.create()


@pytest.fixture()
def valid_investigation_reimbursed_parcels():
    return {
        "name": "2025079971711",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "title": "test_title",
        "summary": "test_summary",
        "instrument": {
            "name": "BL13 - XALOC",
            "code": "BL13"
        },
        "type": "MX",
        "user_list": [
            {"username": "auo-test12", "email": "test_email@<<>>.com", "role": "Principal investigator"},
        ],
        "visit_count": 982,
        "is_reimbursed": True,
        "icat_visit_id": "uo_8623",
        "visa_visit_id": 1008623,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }

@pytest.fixture()
def valid_investigation_industrial():
    return {
        "name": "2025079971722",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "title": "test_title",
        "summary": "test_summary",
        "is_industrial": True,
        "instrument": {
            "name": "BL13 - XALOC",
            "code": "BL13"
        },
        "type": "INDUSTRIAL",
        "user_list": [
            {"username": "auo-test12", "email": "test_email@<<>>.com", "role": "Principal investigator"},
        ],
        "visit_count": 982,
        "is_reimbursed": True,
        "icat_visit_id": "uo_8623",
        "visa_visit_id": 1008623,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }

@pytest.fixture()
def invalid_investigation_industrial():
    return {
        "name": "2025079971733",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "title": "test_title",
        "summary": "test_summary",
        "is_industrial": True,
        "instrument": {
            "name": "BL13 - XALOC",
            "code": "BL13"
        },
        "type": "MX",
        "user_list": [
            {"username": "auo-test12", "email": "test_email@<<>>.com", "role": "Principal investigator"},
        ],
        "visit_count": 982,
        "is_reimbursed": True,
        "icat_visit_id": "uo_8623",
        "visa_visit_id": 1008623,
        "sample_acronyms": ["test_sample_acronym1", "test_sample_acronym2"]
    }