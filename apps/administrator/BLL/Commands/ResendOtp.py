from http import HTTPStatus
from apps.users.models import User, UserVerification
from utils.base_result import BaseResult
from utils.email_sender import send_custom_email
from utils.enum import GroupNames


class ResendOtpCommand:
    """Handles OTP regeneration and sending verification email"""

    @staticmethod
    def execute(email):
        try:
            user = User.objects.get(email=email, is_deleted = False, groups__name=GroupNames.ADMIN.value)
        except User.DoesNotExist:
            return BaseResult(
                status_code=HTTPStatus.NOT_FOUND,
                message="User with this email does not exist"
            )

        verification, created = UserVerification.objects.get_or_create(user=user, is_deleted = False)

        if not verification.is_token_expired():
            return BaseResult(
                status_code=HTTPStatus.BAD_REQUEST,
                message="Otp still valid. Please use the existing code"
            )

        verification.generate_token()
        verification.save()
        
        send_custom_email(
            subject = "Admin Action Verification Code - Aso Oke & Aso Ofi Marketplace",
            recipient_email=user.email,
            message=f"""
            A request was made to perform a sensitive administrative action on your account.

            To proceed, please use the verification code below:

            Verification Code: {verification.token}

            This code expires in 10 minutes.
            If you didn't request this action, please ignore this email and contact support immediately.
            """,
            greeting_name=user.first_name or "Administrator"
        )
        
        return BaseResult(
            status_code=HTTPStatus.OK,
            message="New OTP generated and sent successfully"
        )