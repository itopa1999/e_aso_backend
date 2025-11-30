from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import get_object_or_404, redirect
from urllib.parse import urlencode
from apps.users.models import User, UserVerification
from rest_framework_simplejwt.tokens import RefreshToken
from utils.log_helpers import OperationLogger



class VerifyEmailCommand:
    @staticmethod
    def Execute(uidb64, token, url_email): 
        op = OperationLogger(
            "VerifyEmailCommand",
            email=url_email
        )
        op.start()
        
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, id=uid)
        verification = get_object_or_404(UserVerification, user=user, token=token)
        if verification.is_token_expired():
            op.fail(f"Email verification token expired for {user.email}")
            return redirect(f"{settings.BASE_URL}/verified-email-failed.html?email={verification.user.email}&is_login=false")

        # Check if the user has already been verified
        if verification.is_verified:
            op.fail(f"Email {user.email} already verified")
            return redirect(f"{settings.BASE_URL}/verified-email-failed.html?email={verification.user.email}&is_login=false")
        
        # Activate user
        user.is_active = True
        user.save()

        verification.is_verified = True
        verification.save()
        op.success(f"Email verified for user {user.id}")
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        group_names = ", ".join(user.groups.values_list('name', flat=True))

        # Build redirect with query params
        params = urlencode({
            "access": access_token,
            "refresh": str(refresh),
            "email": user.email,
            "name": user.first_name,
            "group": group_names
        })

        return redirect(f"{settings.BASE_URL}/index.html?{params}")

