from http import HTTPStatus
from apps.users.models import User, UserVerification
from utils.base_result import BaseResult
from utils.email_sender import send_custom_email


class ResendOtpCommand:
    """Handles OTP regeneration and sending verification email"""

    @staticmethod
    def Execute(email):
        try:
            try:
                user = User.objects.get(email=email, is_deleted = False)
            except User.DoesNotExist:
                return BaseResult(
                    status_code=HTTPStatus.NOT_FOUND,
                    message="User with this email does not exist"
                )

            verification, created = UserVerification.objects.get_or_create(user=user, is_deleted = False)

            if verification.is_verified:
                return BaseResult(
                    status_code=HTTPStatus.BAD_REQUEST,
                    message="User is already verified, please login."
                )

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

                    This link expires in 10 minutes.
                    If you didn’t request this login, please ignore this email.
                """,
                greeting_name=user.first_name or "Valued Customer"
            )
            
            return BaseResult(
                status_code=HTTPStatus.OK,
                message="New OTP generated and sent successfully"
            )

        except Exception as e:
            return BaseResult(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Failed to resend OTP: {str(e)}"
            )