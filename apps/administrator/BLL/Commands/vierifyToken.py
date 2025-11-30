
from http import HTTPStatus
from apps.users.models import User, UserVerification
from utils.base_result import BaseResult, BaseResultWithData
from utils.log_helpers import OperationLogger


class AdminVerifyOtpCommand:
    """Handles OTP verification process"""

    @staticmethod
    def execute(token, email):
        op = OperationLogger(
            "AdminVerifyOtpCommand",
            email=email
        )
        op.start()
        
        # Logic to verify the OTP token for the given email
        try:
            user = User.objects.get(email=email, is_deleted = False)
            verification = UserVerification.objects.get(user=user, is_deleted = False)
        except (User.DoesNotExist, UserVerification.DoesNotExist):
            op.fail(f"User or verification record not found for {email}")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.BAD_REQUEST,
                message="User or verification record not found"
            )
        if verification.token != token:
            op.fail(f"Invalid token for {email}")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.BAD_REQUEST,
                message="Invalid token."
            )

        if verification.is_token_expired():
            op.fail(f"Token expired for {email}")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.BAD_REQUEST,
                message="Token has expired. Please request a new one."
            )

        op.success(f"Token verified for {email}")
        return BaseResultWithData(
            data=user,
            status_code=HTTPStatus.OK,
            message="Token verified successfully."
        )
