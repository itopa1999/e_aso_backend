from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.conf import settings
from django.shortcuts import get_object_or_404
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


from .models import User, UserVerification
from .swagger import TaggedAutoSchema
from .serializers import *
# Create your views here.



class RegisterUser(generics.GenericAPIView):
    serializer_class = RegUserSerializer
    swagger_schema = TaggedAutoSchema
    def post(self, request, *args, **kwargs):
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
                reverse('verify-email', kwargs={'uidb64': uidb64, 'token': token})
            )

            # Send the verification email with the token
            send_mail(
                "Your Verification Link",
                f"click the link to verify your email: {verification_link} ",
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

            return Response({"message": "Account created. A verification email has been sent.",
                             "email":user.email}, status=status.HTTP_201_CREATED)

        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    


User = get_user_model()


class VerifyEmailView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, id=uid)
            verification = get_object_or_404(UserVerification, user=user, token=token)
            
            if verification.is_token_expired():
                    return Response({'error': 'Link has expired'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the user has already been verified
            if verification.is_verified:
                return Response({'error': 'Link is already verified'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Activate user
            user.is_active = True
            user.save()

            verification.is_verified = True
            verification.save()

            return Response({"message": "Your email has been verified successfully! please go back to login"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid or expired link."}, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    swagger_schema = TaggedAutoSchema
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
         
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            return Response({"error": "Account is inactive"}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        expiration_time = datetime.fromtimestamp(AccessToken(access_token)["exp"])
        return Response(
            {
                "id": user.id,
                "first_name":user.first_name,
                "email": user.email,
                "refresh": str(refresh),
                "access": access_token,
                "expiry": expiration_time,
            },
            status=status.HTTP_200_OK,
        )
            
