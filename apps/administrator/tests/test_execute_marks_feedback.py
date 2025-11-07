import pytest
from apps.administrator.BLL.Commands.MarkCustomerFeedbackDone import MarkCustomerFeedbackDoneCommand
from apps.administrator.models import CustomerFeedback

from utils.base_result import BaseResult

@pytest.mark.django_db
class TestMarkCustomerFeedbackDone:
    """Tests for MarkCustomerFeedbackDoneCommand"""

    def test_execute_marks_feedback_as_done(self):
        """Should mark an existing feedback as done"""
        feedback = CustomerFeedback.objects.create(
            user="Alice",
            feedback="Great service!",
            rating=5,
            is_done=False
        )

        result = MarkCustomerFeedbackDoneCommand.execute(feedback.id)
        feedback.refresh_from_db()

        assert result.status_code == 200
        assert result.message == "Customer feedback marked as done successfully."
        assert feedback.is_done is True

    def test_execute_returns_error_if_feedback_not_found(self):
        """Should return error when feedback ID does not exist"""
        invalid_id = 9999

        result = MarkCustomerFeedbackDoneCommand.execute(invalid_id)

        assert result.status_code == 40
        assert result.message == "Customer feedback not found."
