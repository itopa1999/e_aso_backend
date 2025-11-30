

from apps.administrator.BLL.Commands.vierifyToken import AdminVerifyOtpCommand
from utils.base_result import BaseResultWithData
from http import HTTPStatus
from apps.users.models import User
from utils.log_helpers import OperationLogger

class ChangePasswordCommand:
    """Handles user change password process"""

    @staticmethod
    def execute(token, email, new_password):
        op = OperationLogger(
            "ChangePasswordCommand",
            email=email
        )
        op.start()
        
        # Logic to verify the user credentials and OTP token
        if len(new_password) < 8:
            op.fail("Password too short (less than 8 characters)")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.BAD_REQUEST,
                message="Password must be at least 8 characters long."
            )
            
        response = AdminVerifyOtpCommand.execute(token, email)
        if response.status_code != 200:
            op.fail(f"OTP verification failed for {email}")
            return BaseResultWithData(
                data=None,
                status_code=response.status_code,
                message=response.message
            )
            
        try:
            user = User.objects.get(email=email, is_deleted = False)
        except User.DoesNotExist:
            op.fail(f"User {email} not found")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.UNAUTHORIZED,
                message="Invalid email."
            )
        user.set_password(new_password)
        user.save()
        op.success(f"Password changed successfully for {email}")
        return BaseResultWithData(
            data=None,
            status_code=HTTPStatus.OK,
            message="Password changed successfully."
        )