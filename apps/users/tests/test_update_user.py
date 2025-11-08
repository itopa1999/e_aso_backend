import pytest
from unittest.mock import patch, MagicMock
from http import HTTPStatus

from apps.users.BBL.Commands.UpdateUser import UpdateUserCommand
from utils.base_result import BaseResult


@pytest.mark.django_db
class TestUpdateUserCommand:

    @patch("apps.users.BBL.Commands.UpdateUser.UserUpdateSerializer")
    def test_successful_update(self, mock_serializer):
        # Mock serializer instance
        mock_instance = MagicMock()
        mock_instance.is_valid.return_value = True
        mock_instance.save.return_value = None
        mock_serializer.return_value = mock_instance

        user = MagicMock()
        update_data = {"first_name": "Lucky", "phone": "08012345678"}

        result = UpdateUserCommand.Execute(user, update_data)

        assert isinstance(result, BaseResult)
        assert result.status_code == HTTPStatus.OK
        assert result.message == "User updated successfully"
        mock_instance.is_valid.assert_called_once()
        mock_instance.save.assert_called_once()

    @patch("apps.users.BBL.Commands.UpdateUser.UserUpdateSerializer")
    def test_update_with_invalid_data_returns_error(self, mock_serializer):
        # Mock invalid serializer
        mock_instance = MagicMock()
        mock_instance.is_valid.return_value = False
        mock_instance.errors = {"email": ["This field is required."]}
        mock_serializer.return_value = mock_instance

        user = MagicMock()
        update_data = {"email": ""}

        result = UpdateUserCommand.Execute(user, update_data)

        assert isinstance(result, BaseResult)
        assert result.status_code == HTTPStatus.BAD_REQUEST
        assert "email" in result.message
        mock_instance.is_valid.assert_called_once()
        mock_instance.save.assert_not_called()

    @patch("apps.users.BBL.Commands.UpdateUser.UserUpdateSerializer")
    def test_partial_update_flag_is_passed(self, mock_serializer):
        user = MagicMock()
        update_data = {"first_name": "Lucky"}

        UpdateUserCommand.Execute(user, update_data)

        # Verify serializer was initialized correctly
        mock_serializer.assert_called_once_with(user, data=update_data, partial=True)
