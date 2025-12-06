from http import HTTPStatus
from apps.users.models import User, UserVerification
from utils.base_result import BaseResult
from utils.email_sender import send_custom_email
from utils.enum import GroupNames
from utils.log_helpers import OperationLogger


class ResendOtpCommand:
    """Handles OTP regeneration and sending verification email"""

    @staticmethod
    def execute(email):
        op = OperationLogger(
            "ResendOtpCommand",
            email=email
        )
        op.start()
        
        try:
            user = User.objects.get(email=email, is_deleted = False)
        except User.DoesNotExist:
            op.fail(f"User {email} not found")
            return BaseResult(
                status_code=HTTPStatus.NOT_FOUND,
                message="User with this email does not exist"
            )

        verification, created = UserVerification.objects.get_or_create(user=user, is_deleted = False)

        # if not verification.is_token_expired():
        #     return BaseResult(
        #         status_code=HTTPStatus.BAD_REQUEST,
        #         message="Otp still valid. Please use the existing code"
        #     )

        verification.generate_token()
        verification.save()
        
        send_custom_email(
            subject = "Action Verification Code - Esther's Fabrics Ofi Marketplace",
            recipient_email=user.email,
            message=f"""
            A request was made to perform a sensitive action on your account.

            To proceed, please use the verification code below:

            Verification Code: {verification.token}

            This code expires in 10 minutes.
            If you didn't request this action, please ignore this email and contact support immediately.
            """,
            greeting_name=user.first_name or "User"
        )
        op.success(f"OTP sent to {email}")
        
        return BaseResult(
            status_code=HTTPStatus.OK,
            message="New OTP generated and sent successfully"
        )