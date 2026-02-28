
from http import HTTPStatus
from django.urls import reverse
import secrets
from apps.users.models import User, UserVerification, MagicLoginToken
from utils.base_result import BaseResult
from utils.email_sender import send_custom_email
from utils.log_helpers import OperationLogger


class ResendVerificationEmailCommand:

    @staticmethod
    def Execute(validatedData, request=None):
        email = validatedData["email"]
        isLogin = validatedData["is_login"]
        
        op = OperationLogger(
            "ResendVerificationEmailCommand",
            email=email,
            is_login=isLogin
        )
        op.start()

        try:
            user = User.objects.get(email=email, is_deleted = False)

            # 🔹 Magic login flow
            if isLogin:
                if not user.is_active:
                    op.fail(f"User {user.id} account is inactive")
                    return BaseResult(
                        message="Account inactive",
                        status_code=HTTPStatus.BAD_REQUEST
                    )

                # ✅ Generate simple random token (URL-safe)
                token = secrets.token_urlsafe(24)
                
                # ✅ Delete old tokens and create fresh one
                MagicLoginToken.objects.filter(user=user).delete()
                magic_token = MagicLoginToken.objects.create(
                    user=user,
                    signed_token=token,
                    is_used=False
                )
                
                # ✅ Build simple link with token and email as query params
                verificationLink = request.build_absolute_uri(
                    reverse("verify-magic-login")
                )
                verificationLink = f"{verificationLink}?token={token}&email={email}"

                send_custom_email(
                    subject="Your Magic Login Link",
                    recipient_email=email,
                    message=f"""
                        Here’s your secure Magic Login Link to access your account:

                        {verificationLink}

                        This link expires in 10 minutes.
                        If you didn’t request this login, please ignore this email.
                    """,
                    greeting_name=user.first_name or "Valued Customer"
                )

                op.success(f"Magic login link resent to {email}")
                return BaseResult(
                    message="A new magic login link sent to email",
                    status_code=HTTPStatus.OK
                )

            # 🔹 Email verification flow
            if user.is_active:
                op.fail(f"Email {email} is already verified")
                return BaseResult(
                    message="Email is already verified.",
                    status_code=HTTPStatus.BAD_REQUEST
                )

            verification, _ = UserVerification.objects.get_or_create(user=user)
            verification.generate_token()
            verification.is_verified = False
            verification.save()

            uidb64 = urlsafe_base64_encode(force_bytes(user.id))
            token = verification.token

            verificationLink = request.build_absolute_uri(
                reverse("verify-email", kwargs={
                    "uidb64": uidb64,
                    "token": token,
                    "url_email": email
                })
            )

            send_custom_email(
                subject="Verify Your Email - Esther's Fabrics Ofi Marketplace",
                recipient_email=user.email,
                message=f"""
                    Please verify your email address by clicking below:

                    {verificationLink}

                    This link expires in 10 minutes.
                    If you didn’t request this, ignore it.
                """,
                greeting_name=user.first_name or "Valued Customer"
            )

            op.success(f"Verification email resent to {email}")
            return BaseResult(
                message="A new verification email has been sent.",
                status_code=HTTPStatus.OK
            )

        except User.DoesNotExist:
            op.fail(f"User with email {email} does not exist")
            return BaseResult(
                message="User with this email does not exist.",
                status_code=HTTPStatus.NOT_FOUND
            )
