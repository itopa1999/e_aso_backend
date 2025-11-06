
from http import HTTPStatus
from apps.users.models import User, UserVerification
from utils.base_result import BaseResult


class AdminVerifyOtpCommand:
    """Handles OTP verification process"""

    @staticmethod
    def execute(token, email):
        # Logic to verify the OTP token for the given email
        try:
            user = User.objects.get(email=email, is_deleted = False)
            verification = UserVerification.objects.get(user=user, is_deleted = False)
        except (User.DoesNotExist, UserVerification.DoesNotExist):
            return BaseResult(
                status_code=HTTPStatus.BAD_REQUEST,
                message="User or verification record not found"
            )
        print(verification.token, token)
        if verification.token != token:
            return BaseResult(
                status_code=HTTPStatus.BAD_REQUEST,
                message="Invalid token."
            )

        if verification.is_token_expired():
            return BaseResult(
                status_code=HTTPStatus.BAD_REQUEST,
                message="Token has expired. Please request a new one."
            )

        return BaseResult(
            status_code=HTTPStatus.OK,
            message="Token verified successfully."
        )
