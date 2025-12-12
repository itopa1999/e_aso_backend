from rest_framework import serializers
from django.contrib.auth.models import Group
from apps.aso.models import Order
from apps.users.models import ContactFormSubmission, Transaction, User
from utils.enum import GroupNames



class RegUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']
        
    def create(self, validated_data):
        user = User.objects.create(
            **validated_data,
            is_active=False,
        )
        
        customer_group, _ = Group.objects.get_or_create(name=GroupNames.CUSTOMER.value)
        user.groups.add(customer_group)
        
        return user
    
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    
class ResendLinkSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    is_login = serializers.BooleanField(required=True)

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone']



class RecentOrderSerializer(serializers.ModelSerializer):
    latest_tracking_status = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['id', 'total', 'order_number', 'latest_tracking_status', 'created_at']
        
    def get_latest_tracking_status(self, obj):
        latest_tracking = obj.tracking_events.order_by('-date').first()
        return latest_tracking.status if latest_tracking else None
        
        
class TransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'transaction_type', 'reference', 'channel', 'status', 'order_id', 'created_at']

class UserOrderSummarySerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    total_orders = serializers.IntegerField()
    referral_code = serializers.CharField()
    is_referral_qualified = serializers.BooleanField()
    total_successful_referrals = serializers.IntegerField()
    referral_used = serializers.BooleanField()
    recent_orders = RecentOrderSerializer(many=True)
    transactions = TransactionsSerializer(many=True)
    
    
class ReferralCodeValidationSerializer(serializers.Serializer):
    referral_code = serializers.CharField(required=True, max_length=20)
    

class ContactFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactFormSubmission
        fields = ['full_name', 'phone', 'email', 'subject', 'message']


class TelegramNotificationSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['activate', 'deactivate'], required=True)
    telegram_user_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        fields = ['action', 'telegram_user_id']