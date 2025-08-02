from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from datetime import datetime
from django.db.models import Q
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode



from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from administrator.utils import generate_magic_token, validate_magic_token


from .models import User, UserVerification
from .swagger import TaggedAutoSchema
from .serializers import *
# Create your views here. 


User = get_user_model()


class VerifyEmailView(APIView):
    swagger_schema = TaggedAutoSchema
    def get(self, request, uidb64, token, url_email):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
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

            return redirect(f"{settings.BASE_URL}/email-verified.html?email={verification.user.email}")
        except Exception as e:
            return redirect(f"{settings.BASE_URL}/verified-email-failed.html?email={url_email}&is_login=false")
    
    
class ResendVerificationEmailView(generics.GenericAPIView):
    serializer_class = ResendLinkSerializer
    swagger_schema = TaggedAutoSchema
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        is_login = serializer.validated_data['is_login']
        
        try:
            user = User.objects.get(email=email)
            
            if is_login:
                if not user.is_active:
                    return Response({"error": "Account inactive"}, status=400)
                uidb64 = urlsafe_base64_encode(force_bytes(user.id))
                token = generate_magic_token(email)

                verification_link = request.build_absolute_uri(
                    reverse('verify-magic-login', kwargs={'uidb64': uidb64, 'token': token, 'url_email': email})
                )
                
                send_mail(
                    subject="Your Magic Login Link",
                    message=f"Click to log in: {verification_link}\nThis link expires in 10 minutes.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False
                )

                return Response({"message": "A new magic login link sent to email"}, status=200)

            if user.is_active:
                return Response({"error": "Email is already verified."}, status=status.HTTP_400_BAD_REQUEST)

            # Generate or reuse verification
            verification, _ = UserVerification.objects.get_or_create(user=user)
            verification.generate_token()
            verification.save()

            uidb64 = urlsafe_base64_encode(force_bytes(user.id))
            token = verification.token

            verification_link = request.build_absolute_uri(
                reverse('verify-email', kwargs={'uidb64': uidb64, 'token': token, 'url_email': email})
            )

            subject = "Verify Your Email - Aso Oke & Aso Ofi Marketplace"
            message = f"""
                Dear {user.first_name or 'Valued Customer'},

                Welcome back to Aso Oke & Aso Ofi Marketplace!

                Please verify your email address by clicking the link below:

                {verification_link}

                This link will expire in 10 minutes. If you didn't request this email, you can safely ignore it.

                Thanks,
                The Aso Oke & Aso Ofi Marketplace Team
                """

            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

            return Response({"message": "A new verification email has been sent."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

            

class SendMagicLinkView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    swagger_schema = TaggedAutoSchema
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            serializer = RegUserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            if serializer.is_valid():
                # Create user
                user = serializer.save()
                verification = UserVerification(user=user)
                verification.generate_token()
                verification.save()
                
                user.is_active = False
                user.save()
                
                token = verification.token
                uidb64 = urlsafe_base64_encode(force_bytes(user.id))
                verification_link = request.build_absolute_uri(
                    reverse('verify-email', kwargs={'uidb64': uidb64, 'token': token, 'url_email': email})
                )
                
                subject = "Verify Your Email - Aso Oke & Aso Ofi Marketplace"
        
                message = f"""
                    Dear {user.first_name or 'Valued Customer'},

                    Welcome to Aso Oke & Aso Ofi Marketplace - Nigeria's premier destination for authentic traditional fabrics and textiles!

                    To complete your registration and access our exclusive marketplace, please verify your email address by clicking the link below:

                    {verification_link}

                    Explore our curated collections:
                    ✨ Handwoven Aso Oke fabrics
                    ✨ Premium Aso Ofi textiles
                    ✨ Traditional embroidery pieces
                    ✨ Custom tailoring services

                    Why verify your email?
                    ✓ Secure your account
                    ✓ Receive order updates
                    ✓ Get exclusive member discounts
                    ✓ Access your purchase history

                    The verification link will expire in 24 hours. If you didn't create an account with us, please ignore this email.

                    Need assistance? Contact our support team:
                    📞 +234 1 700 0000
                    ✉️ support@aso-okemarketplace.ng
                    📍 14 Traditional Weavers Road, Ilorin, Kwara State

                    Preserving Nigeria's textile heritage,
                    The Aso Oke & Aso Ofi Marketplace Team

                    Celebrating Nigeria's Rich Textile Traditions Since 2020
                    """

                # Send the verification email with the token
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                )

                return Response({"message": "Account created. A verification email has been sent.",
                                "email":user.email}, status=status.HTTP_201_CREATED)

        if not user.is_active:
            return Response({"error": "Account inactive"}, status=400)
        
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        token = generate_magic_token(email)

        verification_link = request.build_absolute_uri(
            reverse('verify-magic-login', kwargs={'uidb64': uidb64, 'token': token, 'url_email': email})
        )
        
        send_mail(
            subject="Your Magic Login Link",
            message=f"Click to log in: {verification_link}\nThis link expires in 10 minutes.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False
        )

        return Response({"message": "Magic login link sent to email"}, status=200)
    
    
class MagicLoginView(APIView):
    swagger_schema = TaggedAutoSchema
    def get(self, request, uidb64, token, url_email):
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, id=uid)
        email = validate_magic_token(token)

        if not email:
            return redirect(f"{settings.BASE_URL}/verified-email-failed.html?email={url_email}&is_login=true")

        try:
            user = User.objects.get(id = user.id, email=email)
        except User.DoesNotExist:
            return redirect(f"{settings.BASE_URL}/verified-email-failed.html?email={url_email}&is_login=true")

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Prepare response with cookies
        cookie_settings = settings.COOKIE_SETTINGS
        response = HttpResponseRedirect(f"{settings.BASE_URL}/index.html")
        # Set cookies
        response.set_cookie("access", access_token, max_age=86400, **cookie_settings)       # 1 day
        response.set_cookie("refresh", str(refresh), max_age=604800, **cookie_settings)      # 7 days
        response.set_cookie("email", user.email, max_age=86400, **cookie_settings)
        response.set_cookie("name", user.first_name, max_age=86400, **cookie_settings)

        return response