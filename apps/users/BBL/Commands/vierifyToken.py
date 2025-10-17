from rest_framework import serializers

class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField(max_length=6)


class VerifyOtpView(generics.GenericAPIView):
    serializer_class = VerifyOtpSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        token = serializer.validated_data['token']

        try:
            user = User.objects.get(email=email)
            verification = UserVerification.objects.get(user=user)
        except (User.DoesNotExist, UserVerification.DoesNotExist):
            return Response({"error": "Invalid email or token."},
                            status=status.HTTP_404_NOT_FOUND)

        if verification.is_token_expired():
            return Response({"error": "Token has expired. Please request a new one."},
                            status=status.HTTP_400_BAD_REQUEST)

        if verification.token != token:
            return Response({"error": "Invalid token."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Success
        verification.is_verified = True
        verification.save()

        return Response({"message": "User verified successfully."},
                        status=status.HTTP_200_OK)
