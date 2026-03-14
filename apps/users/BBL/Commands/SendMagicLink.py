from http import HTTPStatus
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import secrets
from apps.users.models import User, UserVerification, MagicLoginToken
from apps.users.serializers import RegUserSerializer
from utils.base_result import BaseResultWithData
from utils.email_sender import send_custom_email
from utils.log_helpers import OperationLogger


class SendMagicLinkCommand:
    @staticmethod
    def Execute(request, validatedData):
        email = validatedData.get("email")
        op = OperationLogger(
            "SendMagicLinkCommand",
            email=email
        )
        op.start()
        
        try:
            user = User.objects.get(email=email, is_deleted = False)
            is_new_user = False
        except User.DoesNotExist:
            is_new_user = True

        if is_new_user:
            serializer = RegUserSerializer(data=validatedData)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            # Create verification record
            verification = UserVerification(user=user)
            verification.generate_token()
            verification.save()

            user.is_active = False
            user.save()

            token = verification.token
            uidb64 = urlsafe_base64_encode(force_bytes(user.id))
            verification_link = request.build_absolute_uri(
                reverse("verify-email", kwargs={"uidb64": uidb64, "token": token, "url_email": email})
            )
            
            send_custom_email(
                subject = "Verify Your Email - Esther's Fabrics Ofi Marketplace",
                recipient_email=user.email,
                message=f"""
                Welcome to Esther's Fabrics Ofi Marketplace!

                Please verify your email by clicking the link below:
                
                {verification_link}

                This link expires in 10 minutes.
                
                Explore our curated collections:
                ✨ Handwoven Aso Oke fabrics
                ✨ Premium Aso Ofi textiles
                ✨ Traditional embroidery pieces
                ✨ Custom tailoring services

                Why verify your email?
                ✅ Secure your account  
                ✅ Receive order updates  
                ✅ Access exclusive member discounts  
                ✅ View and manage your order history 
                
                
                If you didn’t request this login, please ignore this email.
                """,
                greeting_name=user.first_name or "Valued Customer"
            )
            
            op.success(f"New user {user.id} created and verification email sent")
            return BaseResultWithData(
                data={"email": user.email},
                status_code=HTTPStatus.CREATED,
                message="Account created. A verification email has been sent."
            )

        if not user.is_active:
            op.fail(f"User {user.id} account is inactive")
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.BAD_REQUEST,
                message="Account inactive. Please verify your email first."
            )

        # 🔒 Generate simple random token (URL-safe)
        token = secrets.token_urlsafe(24)  # 32 char URL-safe token
        
        # ✅ Delete old tokens for this user to ensure fresh timestamps
        MagicLoginToken.objects.filter(user=user).delete()
        
        # ✅ Create new token (always fresh, never update)
        magic_token = MagicLoginToken.objects.create(
            user=user,
            signed_token=token,
            is_used=False
        )
        
        # ✅ Build simple link with token and email as query params
        verification_link = request.build_absolute_uri(
            reverse("verify-magic-login")
        )
        verification_link = f"{verification_link}?token={token}&email={email}"
        
        send_custom_email(
            subject="Your Magic Login Link",
            recipient_email=email,
            message=f"""
            Welcome back to Esther's Fabrics Ofi Marketplace!

            Click below to log in instantly:
            {verification_link}

            This link expires in 10 minutes.
            If you didn’t request this login, please ignore this email.
            """,
            greeting_name=user.first_name or "Valued Customer"
        )

        op.success(f"Magic login link sent to {email}")
        return BaseResultWithData(
            data={"email": email},
            status_code=HTTPStatus.OK,
            message="Login link sent successfully."
        )

