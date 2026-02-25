from django.conf import settings
from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import MagicLoginToken
from utils.log_helpers import OperationLogger
from apps.users.user_agent_utils import save_user_agent


class MagicLoginCommand:
    @staticmethod
    def Execute(token, email=None, request=None):
        """
        Simplified magic login:
        1. Validate token exists and is not used
        2. Check expiration
        3. Mark as used
        4. Generate JWT tokens
        5. Set cookies
        6. Redirect to index
        """
        op = OperationLogger("MagicLoginCommand", token=token[:10] + "..." if token else "None")
        op.start()
        
        # ✅ Find and validate magic token
        try:
            magic_token = MagicLoginToken.objects.get(signed_token=token, is_used=False)
        except MagicLoginToken.DoesNotExist:
            op.fail("Token not found or already used")
            email_param = f"&email={email}" if email else "&email=unknown"
            return redirect(f"{settings.BASE_URL}/verified-email-failed.html?is_login=true{email_param}")
        
        # ✅ Get user email for error messages
        user_email = magic_token.user.email
        
        # ✅ Check if token expired (10 minutes)
        if magic_token.is_token_expired():
            op.fail("Token expired")
            return redirect(f"{settings.BASE_URL}/verified-email-failed.html?is_login=true&error=expired&email={user_email}")
        
        # ✅ Get user
        user = magic_token.user
        
        # ✅ Mark token as used to prevent replay attacks
        magic_token.mark_used()
        op.success(f"Token marked as used for user {user.id}")
        
        # ✅ Save user agent if request provided
        if request:
            try:
                save_user_agent(user, request)
                op.success(f"User agent saved")
            except Exception as e:
                op.fail(f"Failed to save user agent: {str(e)}")
        
        # ✅ Generate JWT tokens
        op.success(f"Magic login successful for user {user.id}")
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # ✅ Get user groups
        group_names = ",".join(user.groups.values_list("name", flat=True))
        
        # ✅ Create response and set cookies
        # Redirect to index.html without query params - cookies handle auth
        response = redirect(f"{settings.BASE_URL}/index.html")
        
        response.set_cookie(
            'access', 
            value=access_token, 
            max_age=3600,  # 1 hour
            path='/', 
            samesite='Lax',
        )
        response.set_cookie(
            'refresh', 
            value=refresh_token, 
            max_age=2592000,  # 30 days
            path='/', 
            samesite='Lax',
        )
        response.set_cookie(
            'email', 
            value=user.email, 
            max_age=2592000, 
            path='/', 
            samesite='Lax',
        )
        response.set_cookie(
            'name', 
            value=user.first_name or user.get_full_name() or 'User', 
            max_age=2592000, 
            path='/', 
            samesite='Lax',
        )
        response.set_cookie(
            'group', 
            value=group_names, 
            max_age=2592000, 
            path='/', 
            samesite='Lax',
        )
        
        op.success(f"Cookies set and redirecting to index for user {user.id}")
        return response