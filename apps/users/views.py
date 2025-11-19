from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.throttling import ScopedRateThrottle
from apps.users.BBL.Commands.ContactFormSubmission import ContactFormSubmissionCommand
from apps.users.BBL.Commands.MagicLogin import MagicLoginCommand
from apps.users.BBL.Commands.UpdateUser import UpdateUserCommand
from apps.users.BBL.Commands.VerifyEmail import VerifyEmailCommand
from apps.users.BBL.Commands.ValidateReferralCode import ValidateReferralCodeCommand

from apps.users.BBL.Commands.ResendVerificationEmail import ResendVerificationEmailCommand
from apps.users.BBL.Commands.SendMagicLink import SendMagicLinkCommand
from apps.users.BBL.Queries.GetUserProfile import GetUserProfileSummaryQuery
from .serializers import *



# Create your views here.


User = get_user_model()


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def get(self, request, uidb64, token, url_email):
        return VerifyEmailCommand.Execute(uidb64, token, url_email)
    
    
class ResendVerificationEmailView(generics.GenericAPIView):
    serializer_class = ResendLinkSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = ResendVerificationEmailCommand.Execute(
            serializer.validated_data,
            request=request
        )

        return Response(result.to_dict(), status=result.status_code)
        

            

class SendMagicLinkView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "magic_link"
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = SendMagicLinkCommand.Execute(request, serializer.validated_data)
        return Response(result.to_dict(), status=result.status_code)
    
    
class MagicLoginView(APIView):
    
    def get(self, request, uidb64, token, url_email):
        return MagicLoginCommand.Execute(uidb64, token, url_email)
    
    

class UserProfileSummaryView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserOrderSummarySerializer
    def get(self, request):
        result = GetUserProfileSummaryQuery.query(request.user)
        return Response(result.to_dict(), status=result.status_code)


class UpdateUserView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserUpdateSerializer

    def put(self, request):
        result = UpdateUserCommand.Execute(request.user, request.data)
        return Response(result.to_dict(), status=result.status_code)
    
    
class ValidateReferralCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, referral_code, *args, **kwargs):
                
        result = ValidateReferralCodeCommand.execute(request.user, referral_code)
        return Response(result.to_dict(), status=result.status_code)
    


class ContactFormSubmissionView(generics.GenericAPIView):
    serializer_class = ContactFormSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request, *args, **kwargs):
        result = ContactFormSubmissionCommand.execute(request.data)
        return Response(result.to_dict(), status=result.status_code)