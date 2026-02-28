
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
            user = User.objects.get(email=email, is_deleted=False)
            # Use filter().first() to handle soft deletes properly
            verification = UserVerification.objects.filter(user=user, is_deleted=False).first()
            
            if not verification:
                op.fail(f"Verification record not found for {email}")
                return BaseResultWithData(
                    data=None,
                    status_code=HTTPStatus.BAD_REQUEST,
                    message="User or verification record not found"
                )
        except User.DoesNotExist:
            op.fail(f"User not found for {email}")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.BAD_REQUEST,
                message="User or verification record not found"
            )
        
        if verification.token != token:
            # Debug: Log the actual values being compared
            op.fail(f"Invalid token for {email} | Stored: '{verification.token}' (type: {type(verification.token).__name__}) | Received: '{token}' (type: {type(token).__name__})")
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

        # 🔒 Check if token has already been used to prevent replay attacks
        if verification.is_verified:
            op.fail(f"Token already used for {email} - replay attack detected")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.BAD_REQUEST,
                message="Token has already been used. Please request a new one."
            )

        # 🔒 Mark token as used immediately to prevent replay attacks
        verification.is_verified = True
        verification.save()
        op.success(f"Token verified and invalidated for {email}")

        return BaseResultWithData(
            data=user,
            status_code=HTTPStatus.OK,
            message="Token verified successfully."
        )
