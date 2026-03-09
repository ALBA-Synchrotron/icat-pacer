import pytest


@pytest.fixture()
def valid_investigation():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "release_date": "2028-07-02T00:00:00Z",
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
        "is_reimbursed": True
    }

@pytest.fixture()
def investigation_payload_empty_name():
    return {
        "name": "",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "release_date": "2028-07-02T00:00:00Z",
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
        "is_reimbursed": True
    }

@pytest.fixture()
def investigation_payload_empty_facility():
    return {
        "name": "2025079999",
        "facility": None,
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "release_date": "2028-07-02T00:00:00Z",
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
        "is_reimbursed": True
    }

@pytest.fixture()
def investigation_payload_empty_start_date():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": None,
        "end_date": "2025-07-02T00:00:00Z",
        "release_date": "2028-07-02T00:00:00Z",
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
        "is_reimbursed": True
    }

@pytest.fixture()
def investigation_payload_empty_end_date():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": None,
        "release_date": "2028-07-02T00:00:00Z",
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
        "is_reimbursed": True
    }

@pytest.fixture()
def investigation_payload_empty_title():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "release_date": "2028-07-02T00:00:00Z",
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
        "is_reimbursed": True
    }


@pytest.fixture()
def investigation_payload_empty_summary():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "release_date": "2028-07-02T00:00:00Z",
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
        "is_reimbursed": True
    }


@pytest.fixture()
def investigation_payload_empty_instrument():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "release_date": "2028-07-02T00:00:00Z",
        "title": "test_title",
        "summary": "test_summary",
        "instrument": None,
        "type": "MX",
        "user_list": [
            {"username": "testuser", "email": "test_email@<<>>.com", "role": "Principal investigator"},
            {"username": "testuser", "email": "test_email1@<<>>.com", "role": "Local contact"}
        ],
        "visit_count": 1,
        "is_reimbursed": True
    }


@pytest.fixture()
def investigation_payload_empty_type():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "release_date": "2028-07-02T00:00:00Z",
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
        "is_reimbursed": True
    }


@pytest.fixture()
def investigation_payload_invalid_missing_username():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "release_date": "2028-07-02T00:00:00Z",
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
        "is_reimbursed": True
    }

@pytest.fixture()
def investigation_payload_invalid_missing_email():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "release_date": "2028-07-02T00:00:00Z",
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
        "is_reimbursed": True
    }

@pytest.fixture()
def investigation_payload_invalid_missing_role():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "release_date": "2028-07-02T00:00:00Z",
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
        "is_reimbursed": True
    }


@pytest.fixture()
def investigation_payload_invalid_missing_instrument_name():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "release_date": "2028-07-02T00:00:00Z",
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
        "is_reimbursed": True
    }


@pytest.fixture()
def investigation_payload_invalid_missing_instrument_code():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "release_date": "2028-07-02T00:00:00Z",
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
        "is_reimbursed": True
    }


@pytest.fixture()
def valid_investigation():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "release_date": "2028-07-02T00:00:00Z",
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
        "is_reimbursed": True
    }

@pytest.fixture()
def valid_investigation():
    return {
        "name": "2025079999",
        "facility": "ALBA",
        "start_date": "2025-07-01T00:00:00Z",
        "end_date": "2025-07-02T00:00:00Z",
        "release_date": "2028-07-02T00:00:00Z",
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
        "is_reimbursed": True
    }