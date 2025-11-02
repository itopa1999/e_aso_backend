

from apps.administrator.models import CustomerFeedback
from utils.base_result import BaseResult


class MarkCustomerFeedbackDoneCommand:
    @staticmethod
    def execute(feedbackId):
        """Marks the customer feedback as done."""
        try:
            feedback = CustomerFeedback.objects.get(id=feedbackId)
            feedback.is_done = True
            feedback.save()
            return BaseResult(
                message="Customer feedback marked as done successfully.",
                status_code=200,
            )
        except CustomerFeedback.DoesNotExist:
            return BaseResult(
                message="Customer feedback not found.",
                status_code=40,
            )
        