import pytest


@pytest.fixture()
def valid_user():
    return {
        "first_name": "Test",
        "last_name": "Test1",
        "ORCID": "",
        "email": "test1@cells.es",
        "affiliation": {
            "id": 999,
            "name": "AAS",
            "code": "LEL",
            "department_name": "",
            "department_code": "GTS",
            "unit": "The GTS",
            "city": "Cerdanyola del Vallès"
        },
        "is_staff": False,
        "enabled": True,
        "id": 1021,
        "user_list": [
            {
                "username": "auo-test"
            },
            {
                "username": "auo-testTest1-ou"
            }
        ]
    }

@pytest.fixture()
def valid_user_investigation():
    return {
        "first_name": "Test",
        "last_name": "Test1",
        "ORCID": "",
        "email": "test112@cells.es",
        "affiliation": {
            "id": 999,
            "name": "AAS",
            "code": "LEL",
            "department_name": "",
            "department_code": "GTS",
            "unit": "The GTS",
            "city": "Cerdanyola del Vallès"
        },
        "is_staff": False,
        "enabled": True,
        "id": 1021,
        "user_list": [
            {
                "username": "auo-test12"
            },
            {
                "username": "auo-testTest1-ou12"
            }
        ]
    }

@pytest.fixture()
def user_payload_empty_first_name():
    return {
        "first_name": "",
        "last_name": "Test1",
        "ORCID": None,
        "email": "test1@cells.es",
        "affiliation": {
            "id": 999,
            "name": "AAS",
            "code": "LEL",
            "department_name": "",
            "department_code": "GTS",
            "unit": "The GTS",
            "city": "Cerdanyola del Vallès"
        },
        "is_staff": False,
        "enabled": True,
        "id": 1021,
        "user_list": [
            {
                "username": "auo-test"
            },
            {
                "username": "auo-testTest1-ou"
            }
        ]
    }


@pytest.fixture()
def user_payload_empty_last_name():
    return {
        "first_name": "Test",
        "last_name": "",
        "ORCID": None,
        "email": "test1@cells.es",
        "affiliation": {
            "id": 999,
            "name": "AAS",
            "code": "LEL",
            "department_name": "",
            "department_code": "GTS",
            "unit": "The GTS",
            "city": "Cerdanyola del Vallès"
        },
        "is_staff": False,
        "enabled": True,
        "id": 1021,
        "user_list": [
            {
                "username": "auo-test"
            },
            {
                "username": "auo-testTest1-ou"
            }
        ]
    }


@pytest.fixture()
def user_payload_empty_email():
    return {
        "first_name": "Test",
        "last_name": "Test1",
        "ORCID": None,
        "email": "",
        "affiliation": {
            "id": 999,
            "name": "AAS",
            "code": "LEL",
            "department_name": "",
            "department_code": "GTS",
            "unit": "The GTS",
            "city": "Cerdanyola del Vallès"
        },
        "is_staff": False,
        "enabled": True,
        "id": 1021,
        "user_list": [
            {
                "username": "auo-test"
            },
            {
                "username": "auo-testTest1-ou"
            }
        ]
    }


@pytest.fixture()
def user_payload_missing_enabled():
    return {
        "first_name": "Test",
        "last_name": "Test1",
        "ORCID": None,
        "email": "test1@cells.es",
        "affiliation": {
            "id": 999,
            "name": "AAS",
            "code": "LEL",
            "department_name": "",
            "department_code": "GTS",
            "unit": "The GTS",
            "city": "Cerdanyola del Vallès"
        },
        "is_staff": False,
        "id": 1021,
        "user_list": [
            {
                "username": "auo-test"
            },
            {
                "username": "auo-testTest1-ou"
            }
        ]
    }


@pytest.fixture()
def user_payload_missing_id():
    return {
        "first_name": "Test",
        "last_name": "Test1",
        "ORCID": None,
        "email": "test1@cells.es",
        "affiliation": {
            "id": 999,
            "name": "AAS",
            "code": "LEL",
            "department_name": "",
            "department_code": "GTS",
            "unit": "The GTS",
            "city": "Cerdanyola del Vallès"
        },
        "is_staff": False,
        "enabled": True,
        "user_list": [
            {
                "username": "auo-test"
            },
            {
                "username": "auo-testTest1-ou"
            }
        ]
    }


@pytest.fixture()
def user_payload_missing_usernames():
    return {
        "first_name": "Test",
        "last_name": "Test1",
        "ORCID": None,
        "email": "test1@cells.es",
        "affiliation": {
            "id": 999,
            "name": "AAS",
            "code": "LEL",
            "department_name": "",
            "department_code": "GTS",
            "unit": "The GTS",
            "city": "Cerdanyola del Vallès"
        },
        "is_staff": False,
        "enabled": True,
        "id": 1021,
        "user_list": [
        ]
    }


@pytest.fixture()
def user_payload_missing_affiliation():
    return {
        "first_name": "Test",
        "last_name": "Test1",
        "ORCID": None,
        "email": "test1@cells.es",
        "affiliation": {
        },
        "is_staff": False,
        "enabled": True,
        "id": 1021,
        "user_list": [
            {
                "username": "auo-test"
            },
            {
                "username": "auo-testTest1-ou"
            }
        ]
    }
