import pytest

from exceptions.user import UserValidationError
from helpers.contexts.user import create_user_context

@pytest.fixture
def invalid_user_payload(request):
    return request.getfixturevalue(request.param)

class TestUserValidation:



    @pytest.mark.parametrize("invalid_user_payload",
                             [
                                 "user_payload_empty_first_name", "user_payload_empty_last_name",
                                 "user_payload_empty_email", "user_payload_missing_enabled",
                                 "user_payload_missing_id", "user_payload_missing_usernames",
                                 "user_payload_missing_affiliation"
                              ],
                             indirect=True)
    def test_invalid_user_payload(self, invalid_user_payload):
        with pytest.raises(UserValidationError):
            _ = create_user_context(invalid_user_payload)


    def test_valid_user_payload(self, valid_user):
        _ = create_user_context(valid_user)