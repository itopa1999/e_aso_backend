from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.utils.http import urlsafe_base64_decode
from urllib.parse import urlencode
from rest_framework_simplejwt.tokens import RefreshToken
from utils.base_result import BaseResultWithData
from apps.users.models import User
from http import HTTPStatus
from utils.log_helpers import OperationLogger
from apps.users.user_agent_utils import save_user_agent

from utils.magic_link import validate_magic_token


class MagicLoginCommand:
    @staticmethod
    def Execute(uidb64, token, url_email, request=None):
        op = OperationLogger(
            "MagicLoginCommand",
            email=url_email
        )
        op.start()
        
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, id=uid)

        # Validate magic token
        email = validate_magic_token(token)
        if not email or email != user.email:
            op.fail(f"Invalid magic token for {url_email}")
            return redirect(f"{settings.BASE_URL}/verified-email-failed.html?email={url_email}&is_login=true")

        # Save user agent information if request is provided
        if request:
            try:
                save_user_agent(user, request)
                op.success(f"User agent saved for {url_email}")
            except Exception as e:
                op.fail(f"Failed to save user agent: {str(e)}")
                # Don't fail login if user agent saving fails

        op.success(f"Magic login successful for user {user.id}")
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        group_names = ", ".join(user.groups.values_list("name", flat=True))

        params = urlencode({
            "access": access_token,
            "refresh": refresh_token,
            "email": user.email,
            "name": user.first_name,
            "group": group_names
        })

        return redirect(f"{settings.BASE_URL}/index.html?{params}")