

from utils.base_result import BaseResult
from utils.log_helpers import OperationLogger


class CreateCustomerFeedbackCommand:
    @staticmethod
    def execute(serializer):
        """Executes the command to create a new customer feedback."""
        op = OperationLogger(
            "CreateCustomerFeedbackCommand"
        )
        op.start()
        
        feedback = serializer.save()
        op.success(f"Feedback {feedback.id} created successfully")
        return BaseResult (
            message="Feedback submitted successfully",
            status_code=201,
            )
