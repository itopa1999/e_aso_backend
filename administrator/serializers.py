from rest_framework import serializers
from rest_framework.exceptions import ParseError

from administrator.models import User

class RegUserSerializer(serializers.ModelSerializer):
    # full_name = serializers.CharField(required = True)
    class Meta:
        model = User
        fields = ['email']
        
    def create(self, validated_data):
        # full_name = validated_data.pop('full_name')
        # name_parts = full_name.split()

        # first_name = name_parts[0] if name_parts else ""
        # last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else first_name

        user = User.objects.create(
            # first_name=first_name,
            # last_name=last_name,
            **validated_data
        )
        return user
    
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    
class ResendLinkSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    is_login = serializers.BooleanField(required=True)

   