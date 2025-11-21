from apps.users.serializers import ContactFormSerializer
from utils.base_result import BaseResult
from utils.email_sender import send_custom_email


class ContactFormSubmissionCommand:
    @staticmethod
    def execute(data):
        serializer = ContactFormSerializer(data=data)
        if serializer.is_valid():
            contact_submission = serializer.save()
            
            # Send confirmation email
            send_custom_email(
                subject="We've Received Your Message - Aso Oke & Aso Ofi Marketplace",
                recipient_email=contact_submission.email,
                message=f"""
                Thank you for reaching out to us!

                We have successfully received your message and our team will review it shortly. 
                We aim to respond to all inquiries within 24-48 hours.

                Your submitted details:
                • Name: {contact_submission.full_name}
                • Email: {contact_submission.email}
                • Subject: {contact_submission.subject}

                If your matter is urgent, please feel free to reach out to us directly through our support channels.

                We appreciate your interest in Aso Oke & Aso Ofi Marketplace and look forward to assisting you.
                """,
                greeting_name=contact_submission.full_name or "Valued Customer",
            )
            
            return BaseResult (
                message="Contact form submitted successfully.",
                status_code=201,
            )
        else:
            return BaseResult (
                message="Invalid data.",
                status_code=400,
            )