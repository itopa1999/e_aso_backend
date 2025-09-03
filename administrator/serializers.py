from rest_framework import serializers
from rest_framework.exceptions import ParseError

from administrator.models import User
from aso.models import Category, Order, OrderFeedBack, OrderItem, OrderReturn, OrderTracking, PaymentDetail, Product, ProductColor, ProductDetail, ProductImage, ProductSize, ShippingAddress


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



class AdminCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']
        
        
class AdminProductColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductColor
        fields = ['id', 'color_name', 'hex_code']
        
        
class AdminProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ['id', 'size_label']


class AdminProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDetail
        fields = ['id', 'tab', 'title', 'content']


class AdminProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text']
        
        
class ProductSerializer(serializers.ModelSerializer):
    categories = AdminCategorySerializer(many=True, source='category', read_only=True)
    colors = AdminProductColorSerializer(many=True, read_only=True)
    sizes = AdminProductSizeSerializer(many=True, read_only=True)
    details = AdminProductDetailSerializer(many=True, read_only=True)
    images = AdminProductImageSerializer(many=True, read_only=True)
    related_orders = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'product_number',
            'title',
            'description',
            'current_price',
            'original_price',
            'discount_percent',
            'rating',
            'reviews_count',
            'badge',
            'main_image',
            'display_product',
            'created_at',
            'updated_at',
            'categories',
            'colors',
            'sizes',
            'details',
            'images',
            "related_orders"
        ]
        
    def get_related_orders(self, obj):
        # Get all orders that have this product in their order items
        orders = Order.objects.filter(items__product=obj).distinct()
        return DashboardOrderSerializer(orders, many=True).data



# Orders

class AdminProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_number', 'title', 'current_price', 'main_image']


class AdminOrderItemSerializer(serializers.ModelSerializer):
    product = AdminProductSerializer()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'total_price', 'desc']

    def get_total_price(self, obj):
        return obj.total_price()


class AdminShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['first_name', 'last_name', 'address', 'apartment', 'city', 'state', 'phone', 'alt_phone']


class AdminPaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentDetail
        fields = ['method']


class AdminOrderTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTracking
        fields = ['status', 'date', 'description']


class AdminOrderFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderFeedBack
        fields = ['stars', 'comment', 'created_at']


class AdminOrderReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderReturn
        fields = ['reason', 'message', 'created_at']


class AdminOrderDetailSerializer(serializers.ModelSerializer):
    items = AdminOrderItemSerializer(many=True, read_only=True)
    shipping_address = AdminShippingAddressSerializer(read_only=True)
    payment_detail = AdminPaymentDetailSerializer(read_only=True)
    timeline = AdminOrderTrackingSerializer(many=True, read_only=True, source="tracking_events")
    feedback = AdminOrderFeedbackSerializer(many=True, read_only=True)
    return_product = AdminOrderReturnSerializer(many=True, read_only=True)
    customer_first_name = serializers.SerializerMethodField()
    customer_last_name = serializers.SerializerMethodField()
    customer_phone = serializers.SerializerMethodField()
    customer_email = serializers.SerializerMethodField()
    latest_tracking_status = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'other_info', 'subtotal', 'shipping_fee', 'discount', 'total', 'customer_first_name', 'customer_email',
            'tracking_number', 'carrier', 'delivery_date', 'estimated_delivery_date', 'created_at', 'customer_last_name', 'customer_phone',
            'items', 'shipping_address', 'payment_detail', 'timeline', 'feedback', 'return_product', 'latest_tracking_status'
        ]
        
    def get_customer_first_name(self, obj):
        return obj.user.first_name if obj.user and obj.user.first_name else "Not Set"

    def get_customer_last_name(self, obj):
        return obj.user.last_name if obj.user and obj.user.last_name else "Not Set"
    
    def get_customer_phone(self, obj):
        return obj.user.phone if obj.user and obj.user.phone else "Not Set"
    
    def get_customer_email(self, obj):
        return obj.user.email if obj.user and obj.user.email else "Not Set"
    
    def get_latest_tracking_status(self, obj):
        latest_tracking = obj.tracking_events.order_by('-date').first()
        return latest_tracking.status if latest_tracking else None

from django.utils import timezone
class OrderTrackingUpdateSerializer(serializers.Serializer):
    order_number = serializers.CharField()
    new_status = serializers.ChoiceField(choices=OrderTracking.STATUS_CHOICES)
    comment = serializers.CharField()

    def validate_order_number(self, value):
        if not Order.objects.filter(order_number=value).exists():
            raise serializers.ValidationError("Order not found.")
        return value

    def update_status(self):
        order_number = self.validated_data['order_number']
        new_status = self.validated_data['new_status']
        comment = self.validated_data['comment']

        order = Order.objects.get(order_number=order_number)

        # Create new tracking entry
        new_tracking = OrderTracking.objects.create(
            order=order,
            status=new_status,
            date=timezone.now(),
            description=comment,
        )
        return new_tracking
    
    
    
class CustomerOrderSerializer(serializers.ModelSerializer):
    latest_tracking_status = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['order_number', 'latest_tracking_status', 'total']
        
    def get_latest_tracking_status(self, obj):
        latest_tracking = obj.tracking_events.order_by('-date').first()
        return latest_tracking.status if latest_tracking else None
    
    

class UserOrderListSerializer(serializers.ModelSerializer):
    orders = CustomerOrderSerializer(many=True, read_only=True)
    groups = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'orders', 'groups', 'date_joined', 'rider_number']
        
    def get_groups(self, obj):
        return list(obj.groups.values_list('name', flat=True))
        
    