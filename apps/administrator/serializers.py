from rest_framework import serializers
from rest_framework.exceptions import ParseError

from apps.aso.models import Category, LookUp, Order, OrderFeedBack, OrderItem, OrderReturn, OrderTracking, PaymentDetail, Product, ProductColor, ProductDetail, ProductImage, ProductSize, ShippingAddress
from apps.users.models import User
from utils.enum import LookUpsCategories



        
class ResendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

        
        
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
        orders = Order.objects.filter(items__product=obj, is_deleted = False).distinct()
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
        if not Order.objects.filter(order_number=value, is_deleted = False).exists():
            raise serializers.ValidationError("Order not found.")
        return value

    def update_status(self):
        order_number = self.validated_data['order_number']
        new_status = self.validated_data['new_status']
        comment = self.validated_data['comment']

        order = Order.objects.get(order_number=order_number, is_deleted = False)

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
        
    






class BulkUpdateBadgesSerializer(serializers.Serializer):
    badge = serializers.ChoiceField(
        choices=[
            ('New', 'New'),
            ('Best Seller', 'Best Seller'), 
            ('Limited', 'Limited'),
            ('', 'Remove Badge')
        ],
        required=True,
        help_text="The badge to assign to products"
    )
    product_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        default=[],
        help_text="List of product IDs to update"
    )
    product_titles = serializers.ListField(
        child=serializers.CharField(max_length=255),
        required=False, 
        default=[],
        help_text="List of product titles to update"
    )

    def validate(self, data):
        """
        Validate that at least one of product_ids or product_titles is provided
        """
        product_ids = data.get('product_ids', [])
        product_titles = data.get('product_titles', [])
        
        if not product_ids and not product_titles:
            raise serializers.ValidationError(
                "Either product_ids or product_titles must be provided"
            )
        
        return data

    def validate_product_ids(self, value):
        """
        Validate that product IDs exist in database
        """
        if value:
            existing_ids = set(Product.objects.filter(
                id__in=value, is_deleted = False
            ).values_list('id', flat=True))
            
            non_existing_ids = set(value) - existing_ids
            
            if non_existing_ids:
                raise serializers.ValidationError(
                    f"Products with these IDs do not exist: {list(non_existing_ids)}"
                )
        return value

    def validate_product_titles(self, value):
        """
        Validate that product titles exist in database
        """
        if value:
            existing_titles = set(Product.objects.filter(
                title__in=value, is_deleted = False
            ).values_list('title', flat=True))
            
            non_existing_titles = set(value) - existing_titles
            
            if non_existing_titles:
                raise serializers.ValidationError(
                    f"Products with these titles do not exist: {list(non_existing_titles)}"
                )
        return value


class ImportProductColorSerializer(serializers.Serializer):
    name = serializers.CharField()
    hex = serializers.CharField()

class ImportProductDetailSerializer(serializers.Serializer):
    tab = serializers.ChoiceField(choices=["description", "details", "shipping"])
    content = serializers.CharField()

    
    
class ProductImportSerializer(serializers.Serializer):
    title = serializers.CharField()
    badge = serializers.CharField()
    description = serializers.CharField()
    original_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = serializers.IntegerField(required=False)
    rating = serializers.FloatField()
    category = serializers.ListField(child=serializers.CharField())
    sizes = serializers.ListField(child=serializers.CharField())
    colors = ImportProductColorSerializer(many=True)
    details = ImportProductDetailSerializer(many=True)

    def create(self, validated_data):
        from decimal import Decimal

        category_names = validated_data.pop('category')
        size_list = validated_data.pop('sizes')
        color_list = validated_data.pop('colors')
        details_list = validated_data.pop('details')
        badge_name = validated_data.pop('badge', None)
        

        # Handle categories
        product = Product.objects.create(
            title=validated_data['title'],
            description=validated_data['description'],
            original_price=validated_data['original_price'],
            discount_percent=validated_data.get('discount_percent'),
            rating=validated_data['rating'],
            display_product = False
        )
        for cat_name in category_names:
            try:
                lookup_category = LookUpsCategories.PRODUCT_CATEGORY

                existing_lookup = LookUp.objects.filter(
                    category=lookup_category,
                    name__iexact=cat_name.strip(),
                    is_deleted = False
                ).first()

                if existing_lookup:
                    product.category.add(existing_lookup)
                else:
                    new_lookup = LookUp.objects.create(
                        name=cat_name.strip(),
                        category=lookup_category
                    )
                    product.category.add(new_lookup)
                    print(f"✅ Created new lookup '{cat_name}' under category '{lookup_category}'")

            except LookUp.DoesNotExist:
                print(f"⚠️ Skipping category '{cat_name}' — lookup category not found.")
                continue
            
        if badge_name:
            try:
                lookup_category = LookUpsCategories.BADGE_CATEGORY

                existing_badge = LookUp.objects.filter(
                    category=lookup_category,
                    name__iexact=badge_name.strip(),
                    is_deleted = False
                ).first()

                if existing_badge:
                    product.badge = existing_badge.name
                else:
                    new_badge = LookUp.objects.create(
                        name=badge_name.strip(),
                        category=lookup_category
                    )
                    product.badge = new_badge.name
                    print(f"✅ Created new badge '{badge_name}' under category '{lookup_category}'")

                product.save()

            except LookUp.DoesNotExist:
                print(f"⚠️ Skipping badge '{badge_name}' — lookup category not found.")



        # Handle sizes
        for size_label in size_list:
            ProductSize.objects.create(product=product, size_label=size_label)

        # Handle colors
        for color in color_list:
            ProductColor.objects.create(product=product, color_name=color['name'], hex_code=color.get('hex'))

        # Handle details
        for detail in details_list:
            ProductDetail.objects.create(
                product=product,
                tab=detail['tab'],
                title=detail['tab'].capitalize(),
                content=detail['content']
            )

        return product

