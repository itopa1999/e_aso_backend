from apps.users.serializers import ContactFormSerializer
from utils.base_result import BaseResult
from utils.email_sender import send_custom_email
from utils.log_helpers import OperationLogger


class ContactFormSubmissionCommand:
    @staticmethod
    def execute(data):
        op = OperationLogger(
            "ContactFormSubmissionCommand",
            email=data.get("email"),
            subject=data.get("subject")
        )
        op.start()
        
        serializer = ContactFormSerializer(data=data)
        if serializer.is_valid():
            contact_submission = serializer.save()
            
            # Send confirmation email
            send_custom_email(
                subject="We've Received Your Message - Esther's Fabrics Ofi Marketplace",
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

                We appreciate your interest in Esther's Fabrics Ofi Marketplace and look forward to assisting you.
                """,
                greeting_name=contact_submission.full_name or "Valued Customer",
            )
            op.success(f"Contact form submitted by {contact_submission.email}")
            
            return BaseResult (
                message="Contact form submitted successfully.",
                status_code=201,
            )
        else:
            op.fail(f"Contact form validation failed: {serializer.errors}")
            return BaseResult (
                message="Invalid data.",
                status_code=400,
            )