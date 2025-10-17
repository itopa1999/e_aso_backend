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
import textwrap
from urllib.parse import urlencode

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from apps.aso.models import OrderTracking, Product
from apps.aso.serializers import OrderSerializer
from utils.magic_link import generate_magic_token, validate_magic_token
from utils.email_sender import send_custom_email

from .serializers import *



# Create your views here.


User = get_user_model()


class VerifyEmailView(APIView):
    # swagger_schema = TaggedAutoSchema
    def get(self, request, uidb64, token, url_email):
        "pass"
    
    
class ResendVerificationEmailView(generics.GenericAPIView):
    serializer_class = ResendLinkSerializer
    # swagger_schema = TaggedAutoSchema
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
                
                send_custom_email(
                    subject="Your Magic Login Link",
                    recipient_email=email,
                    message=f"""
                        Here’s your secure **Magic Login Link** to access your Aso Oke & Aso Ofi Marketplace account:

                        {verification_link}

                        This link will expire in **10 minutes** for your security.
                        If you did not request this login, please ignore this email.
                    """,
                    greeting_name=user.first_name or "Valued Customer"
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
            
            send_custom_email(
                subject = "Verify Your Email - Aso Oke & Aso Ofi Marketplace",
                recipient_email=user.email,
                message=f"""
                Welcome back to Aso Oke & Aso Ofi Marketplace!

                Please verify your email address by clicking the link below:

                {verification_link}

                This link will expire in 10 minutes. 
                If you didn't request this email, you can safely ignore it.
                """,
                greeting_name=user.first_name or "Valued Customer"
            )
            return Response({"message": "A new verification email has been sent."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

            

class SendMagicLinkView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    # swagger_schema = TaggedAutoSchema
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
        
                message = textwrap.dedent(f"""
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
                    ✅ Secure your account  
                    ✅ Receive order updates  
                    ✅ Access exclusive member discounts  
                    ✅ View and manage your order history 

                    The verification link will expire in 24 hours. If you didn't create an account with us, please ignore this email.

                    Need assistance? Contact our support team:
                    📞 +234 1 700 0000
                    ✉️ support@aso-okemarketplace.ng
                    📍 14 Traditional Weavers Road, Ilorin, Kwara State

                    Preserving Nigeria's textile heritage,
                    The Aso Oke & Aso Ofi Marketplace Team

                    Celebrating Nigeria's Rich Textile Traditions Since 2020
                    """)

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
            message=textwrap.dedent(f"""
                Dear {user.first_name or 'Valued Customer'},

                Welcome back to Aso Oke & Aso Ofi Marketplace!

                Please verify your email address by clicking the link below:

                {verification_link}

                This link will expire in 10 minutes. If you didn't request this email, you can safely ignore it.

                Thanks,
                The Aso Oke & Aso Ofi Marketplace Team
                """),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False
        )

        return Response({"message": "Magic login link sent to email"}, status=200)
    
    
class MagicLoginView(APIView):
    # swagger_schema = TaggedAutoSchema
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
    
    

class UserProfileSummaryView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserOrderSummarySerializer
    # swagger_schema = TaggedAutoSchema
    def get(self, request):
        user = request.user
        orders = Order.objects.filter(user=user).order_by('-created_at')
        data = {
            'first_name': user.first_name or "Not set",
            'last_name': user.last_name or "Not set",
            'email': user.email,
            'phone':user.phone or "Not set",
            'total_orders': orders.count(),
            'recent_orders': orders[:5]
        }
        serializer = UserOrderSummarySerializer(data)
        return Response(serializer.data)


class UpdateUserView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserUpdateSerializer
    # swagger_schema = TaggedAutoSchema

    def put(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "User updated successfully",
            }, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

class ResendOtpView(generics.GenericAPIView):
    serializer_class = ResendOtpSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."},
                            status=status.HTTP_404_NOT_FOUND)

        verification, created = UserVerification.objects.get_or_create(user=user)

        if verification.is_verified:
            return Response({"error": "User is already verified."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Only resend if expired
        if not verification.is_token_expired():
            return Response({"error": "OTP still valid. Please use the existing code."},
                            status=status.HTTP_400_BAD_REQUEST)

        verification.generate_token()
        verification.save()

        subject = "Admin Action Verification Code - Aso Oke & Aso Ofi Marketplace"

        message = textwrap.dedent(f"""
            Dear {user.first_name or user.username},

            A request was made to perform a sensitive administrative action on your account.

            To proceed, please use the verification code below:

            Verification Code: {verification.token}

            ⚠️ For security reasons, this code is valid for 10 minutes only. 
            If you did not initiate this request, please ignore this email and ensure your account remains secure.

            Best regards,  
            Security Team  
            Aso Oke & Aso Ofi Marketplace
            """)


        # Send the verification email with the token
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        return Response({"message": "New OTP generated and sent."},
                        status=status.HTTP_200_OK)
