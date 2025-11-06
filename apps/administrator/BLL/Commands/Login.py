

from http import HTTPStatus
from apps.administrator.BLL.Commands.vierifyToken import AdminVerifyOtpCommand
from utils.base_result import BaseResultWithData
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class LoginCommand:
    """Handles user login process"""

    @staticmethod
    def execute(token, email, password):
        # Logic to verify the user credentials and OTP token
        
        response = AdminVerifyOtpCommand.execute(token, email)
        if response.status_code != 200:
            return BaseResultWithData(
                data=None,
                status_code=response.status_code,
                message=response.message
            )
        
        # Authenticate user
        user = authenticate(email=email, password=password)

        if user is None:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.UNAUTHORIZED,
                message="Invalid email or password."
            )

        # Optional: check if user is active
        if not user.is_active:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.FORBIDDEN,
                message="User account is inactive."
            )

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
        
        return BaseResultWithData(
            data=response_data,
            status_code=HTTPStatus.OK,
            message="Login successful."
        )