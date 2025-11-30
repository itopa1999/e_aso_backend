

from apps.administrator.models import CustomerFeedback
from utils.base_result import BaseResult
from utils.log_helpers import OperationLogger


class MarkCustomerFeedbackDoneCommand:
    @staticmethod
    def execute(feedbackId):
        """Marks the customer feedback as done."""
        op = OperationLogger(
            "MarkCustomerFeedbackDoneCommand",
            feedback_id=feedbackId
        )
        op.start()
        
        try:
            feedback = CustomerFeedback.objects.get(id=feedbackId)
            feedback.is_done = True
            feedback.save()
            op.success(f"Feedback {feedbackId} marked as done")
            return BaseResult(
                message="Customer feedback marked as done successfully.",
                status_code=200,
            )
        except CustomerFeedback.DoesNotExist:
            op.fail(f"Feedback {feedbackId} not found")
            return BaseResult(
                message="Customer feedback not found.",
                status_code=40,
            )
        