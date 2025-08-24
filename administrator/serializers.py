from rest_framework import serializers
from rest_framework.exceptions import ParseError

from administrator.models import User
from aso.models import Order, OrderItem, Product


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
            **validated_data,
        )
        return user
    
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    
class ResendLinkSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    is_login = serializers.BooleanField(required=True)



class RecentOrderSerializer(serializers.ModelSerializer):
    latest_tracking_status = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['id', 'total', 'order_number', 'latest_tracking_status', 'created_at']
        
    def get_latest_tracking_status(self, obj):
        latest_tracking = obj.tracking_events.order_by('-date').first()
        return latest_tracking.status if latest_tracking else None
        
        
class UserOrderSummarySerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    total_orders = serializers.IntegerField()
    recent_orders = RecentOrderSerializer(many=True)
    

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone']
        
        
# ADMIN SERIALIZER

class DashboardOrderSerializer(serializers.ModelSerializer):
    customer_first_name = serializers.CharField(source='user.first_name')
    customer_last_name = serializers.CharField(source='user.last_name')
    amount = serializers.DecimalField(source='total', max_digits=10, decimal_places=2)
    latest_tracking_status = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['id','order_number', 'customer_first_name','customer_last_name', 'delivery_date', 'latest_tracking_status', 'amount']

    
    def get_latest_tracking_status(self, obj):
        latest_tracking = obj.tracking_events.order_by('-date').first()
        return latest_tracking.status if latest_tracking else None

class DashboardTopProductSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='product.title', read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    sold_count = serializers.IntegerField()

    class Meta:
        model = OrderItem
        fields = ['title', 'product_id', 'sold_count']


class DashboardSerializer(serializers.Serializer):
    stats = serializers.DictField()
    order_status = serializers.DictField()
    recent_orders = DashboardOrderSerializer(many=True)
    top_products = DashboardTopProductSerializer(many=True)
