

from utils.base_result import BaseResult


class CreateCustomerFeedbackCommand:
    @staticmethod
    def execute(serializer):
        """Executes the command to create a new customer feedback."""
        feedback = serializer.save()
        return BaseResult (
            message="Feedback submitted successfully",
            status_code=201,
            )
