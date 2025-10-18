
from http import HTTPStatus
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from apps.users.models import User, UserVerification
from utils.base_result import BaseResult
from utils.email_sender import send_custom_email
from utils.magic_link import generate_magic_token


class ResendVerificationEmailCommand:

    @staticmethod
    def Execute(validatedData, request=None):
        email = validatedData["email"]
        isLogin = validatedData["is_login"]

        try:
            user = User.objects.get(email=email)

            # 🔹 Magic login flow
            if isLogin:
                if not user.is_active:
                    return BaseResult(
                        message="Account inactive",
                        status_code=HTTPStatus.BAD_REQUEST
                    )

                uidb64 = urlsafe_base64_encode(force_bytes(user.id))
                token = generate_magic_token(email)

                verificationLink = request.build_absolute_uri(
                    reverse("verify-magic-login", kwargs={
                        "uidb64": uidb64,
                        "token": token,
                        "url_email": email
                    })
                )

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

                return BaseResult(
                    message="A new magic login link sent to email",
                    status_code=HTTPStatus.OK
                )

            # 🔹 Email verification flow
            if user.is_active:
                return BaseResult(
                    message="Email is already verified.",
                    status_code=HTTPStatus.BAD_REQUEST
                )

            verification, _ = UserVerification.objects.get_or_create(user=user)
            verification.generate_token()
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
                subject="Verify Your Email - Aso Oke & Aso Ofi Marketplace",
                recipient_email=user.email,
                message=f"""
                    Please verify your email address by clicking below:

                    {verificationLink}

                    This link expires in 10 minutes.
                    If you didn’t request this, ignore it.
                """,
                greeting_name=user.first_name or "Valued Customer"
            )

            return BaseResult(
                message="A new verification email has been sent.",
                status_code=HTTPStatus.OK
            )

        except User.DoesNotExist:
            return BaseResult(
                message="User with this email does not exist.",
                status_code=HTTPStatus.NOT_FOUND
            )
