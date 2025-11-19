from apps.users.serializers import ContactFormSerializer
from utils.base_result import BaseResult


class ContactFormSubmissionCommand:
    @staticmethod
    def execute(data):
        serializer = ContactFormSerializer(data=data)
        if serializer.is_valid():
            contact_submission = serializer.save()
            return BaseResult (
                message="Contact form submitted successfully.",
                status_code=201,
            )
        else:
            return BaseResult (
                message="Invalid data.",
                status_code=400,
            )