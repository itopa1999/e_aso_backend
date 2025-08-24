from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.shortcuts import get_object_or_404, redirect
from urllib.parse import urlencode
from administrator.models import User, UserVerification
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken



class VerifyEmailCommand:

    @staticmethod
    def verify_email(uidb64, token, url_email): 
        try:
            uid = urlsafe_base64_encode(uidb64).decode()
            user = get_object_or_404(User, id=uid)
            verification = get_object_or_404(UserVerification, user=user, token=token)
            if verification.is_token_expired():
                return redirect(f"{settings.BASE_URL}/verified-email-failed.html?email={verification.user.email}&is_login=false")

            # Check if the user has already been verified
            if verification.is_verified:
                return redirect(f"{settings.BASE_URL}/verified-email-failed.html?email={verification.user.email}&is_login=false")
            
            # Activate user
            user.is_active = True
            user.save()

            verification.is_verified = True
            verification.save()
            
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

        except Exception as e:
            return redirect(f"{settings.BASE_URL}/verified-email-failed.html?email={url_email}&is_login=false")