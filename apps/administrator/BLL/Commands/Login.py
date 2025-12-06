

from http import HTTPStatus
from apps.administrator.BLL.Commands.vierifyToken import AdminVerifyOtpCommand
from utils.base_result import BaseResultWithData
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from utils.log_helpers import OperationLogger
from apps.users.user_agent_utils import save_user_agent


class LoginCommand:
    """Handles user login process"""

    @staticmethod
    def execute(token, email, password, request=None):
        op = OperationLogger(
            "AdminLoginCommand",
            email=email
        )
        op.start()
        
        # Logic to verify the user credentials and OTP token
        
        response = AdminVerifyOtpCommand.execute(token, email)
        if response.status_code != 200:
            op.fail(f"OTP verification failed for {email}")
            return BaseResultWithData(
                data=None,
                status_code=response.status_code,
                message=response.message
            )
        
        # Authenticate user
        user = authenticate(email=email, password=password)

        if user is None:
            op.fail(f"Invalid credentials for {email}")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.UNAUTHORIZED,
                message="Invalid email or password."
            )

        # Optional: check if user is active
        if not user.is_active:
            op.fail(f"User {email} account is inactive")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.FORBIDDEN,
                message="User account is inactive."
            )

        # Save user agent information if request is provided
        if request:
            try:
                save_user_agent(user, request)
                op.success(f"User agent saved for {email}")
            except Exception as e:
                op.fail(f"Failed to save user agent: {str(e)}")
                # Don't fail login if user agent saving fails

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Construct response
        response_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "email": user.email,
            "first_name": user.first_name or "",
        }
        
        op.success(f"Admin {email} logged in successfully")
        return BaseResultWithData(
            data=response_data,
            status_code=HTTPStatus.OK,
            message="Login successful."
        )