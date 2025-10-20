from rest_framework import serializers

from apps.aso.models import Order


class RiderProfileSerializer(serializers.Serializer):
    name = serializers.CharField()
    rider_id = serializers.CharField()
    deliveries_count = serializers.IntegerField()


class RiderOrderSerializer(serializers.ModelSerializer):
    customer_first_name = serializers.CharField(source='user.first_name')
    customer_last_name = serializers.CharField(source='user.last_name')
    amount = serializers.DecimalField(source='total', max_digits=10, decimal_places=2)

    class Meta:
        model = Order
        fields = ['order_number', 'customer_first_name','customer_last_name', 'delivery_date', 'amount']



class RiderDashboardSerializer(serializers.Serializer):
    profile = RiderProfileSerializer()
    recent_deliveries = RiderOrderSerializer(many=True)
    
    
class SendOtpSerializer(serializers.Serializer):
    order_number = serializers.CharField(required=True)


class VerifyOtpSerializer(serializers.Serializer):
    order_number = serializers.CharField(required=True)
    otp = serializers.IntegerField(required=True)
    
    
class RiderOderDetailsSerializer(serializers.Serializer):
    order_number = serializers.CharField(required=True)
    
class MarkOrderAsDeliveredSerializer(serializers.Serializer):
    order_number = serializers.CharField(required=True)
    delivery_notes = serializers.CharField(required=False, allow_blank=True)
    stars = serializers.IntegerField(required=True)
    
    
