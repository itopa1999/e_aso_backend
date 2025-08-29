from rest_framework import serializers
from rest_framework.exceptions import ParseError

from administrator.models import User
from aso.models import Category, Order, OrderItem, Product, ProductColor, ProductDetail, ProductImage, ProductSize


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
