import pytest
from unittest.mock import MagicMock
from apps.administrator.BLL.Commands.CreateCustomerFeedback import CreateCustomerFeedbackCommand
from apps.administrator.models import CustomerFeedback
from utils.base_result import BaseResult


@pytest.mark.django_db
class TestCreateCustomerFeedbackCommand:
    def test_execute_creates_feedback_and_returns_base_result(self):
        """Should call serializer.save() and return a success BaseResult"""

        # Mock serializer that simulates saving feedback
        mock_feedback = CustomerFeedback.objects.create(
            user="John Doe",
            feedback="Excellent service!",
            rating=5
        )
        serializer = MagicMock()
        serializer.save.return_value = mock_feedback

        # Execute the command
        result = CreateCustomerFeedbackCommand.execute(serializer)

        # ✅ Assertions
        assert isinstance(result, BaseResult)
        assert result.message == "Feedback submitted successfully"
        assert result.status_code == 201

        # Ensure serializer.save() was called once
        serializer.save.assert_called_once()

        # Ensure the feedback exists in DB
        feedback_obj = CustomerFeedback.objects.first()
        assert feedback_obj.user == "John Doe"
        assert feedback_obj.feedback == "Excellent service!"
        assert feedback_obj.rating == 5
        assert feedback_obj.is_done is False
