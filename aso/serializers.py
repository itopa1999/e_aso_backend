from rest_framework import serializers
from .models import Cart, CartItem, Category, Order, OrderItem, OrderTracking, PaymentDetail, Product, ProductColor, ProductDetail, ProductImage, ProductSize, ShippingAddress, WatchList
from django.utils.timesince import timesince

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.title')
    product_image = serializers.SerializerMethodField()
    product_id = serializers.IntegerField(source = 'product.id')
    class Meta:
        model = OrderItem
        fields = ['product_name', 'product_id', 'price', 'quantity', 'product_image']
        
    def get_product_image(self, obj):
        request = self.context.get('request')
        if obj.product.main_image and hasattr(obj.product.main_image, 'url'):
            return request.build_absolute_uri(obj.product.main_image.url)
        return None
    
        
class OrderTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTracking
        fields = ['status', 'date', 'description', 'completed']
        
        
class OrderSerializer(serializers.ModelSerializer):
    order_status = serializers.SerializerMethodField()
    order_items = serializers.SerializerMethodField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    shipping = serializers.DecimalField(source='shipping_fee', max_digits=10, decimal_places=2)
    discount = serializers.DecimalField(max_digits=10, decimal_places=2)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'created_at', 'order_status',
            'order_items', 'subtotal', 'shipping', 'discount', 'total'
        ]

    def get_order_status(self, obj):
        latest_status = obj.tracking_events.order_by('-id').first()
        return latest_status.status if latest_status else "placed"

    def get_order_items(self, obj):
        items = obj.items.all()
        item_data = OrderItemSerializer(items[:3], many=True, context=self.context).data
        return item_data


class ShippingAddressSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = ShippingAddress
        exclude = ['id', 'order']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class PaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentDetail
        exclude = ['id', 'order']
        
        
class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    tracking = OrderTrackingSerializer(source='tracking_events', many=True, read_only=True)
    order_status = serializers.SerializerMethodField()
    shipping_address = ShippingAddressSerializer()
    payment_detail = PaymentDetailSerializer()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'created_at', 'subtotal', 'shipping_fee', 'discount',
            'total', 'tracking_number', 'carrier','order_status', 'estimated_delivery_date',
            'items', 'tracking', 'shipping_address', 'payment_detail'
        ]
    
    def get_order_status(self, obj):
        latest_status = obj.tracking_events.order_by('-id').first()
        return latest_status.status if latest_status else "placed"
    

class WatchlistProductSerializer(serializers.ModelSerializer):
    current_price = serializers.SerializerMethodField()
    short_description = serializers.SerializerMethodField()
    watchlisted = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'short_description',
            'badge',
            'main_image',
            'current_price',
            'original_price',
            'discount_percent',
            'rating',
            'reviews_count',
            'watchlisted'
        ]
    
    def get_current_price(self, obj):
        return float(obj.current_price)
    
    def get_short_description(self, obj):
        return obj.description[:80] + "..." if len(obj.description) > 80 else obj.description
    
    def get_watchlisted(self, obj):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            return WatchList.objects.filter(user=request.user, product=obj).exists()
        return False

    

class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id")
    product_title = serializers.CharField(source="product.title")
    product_price = serializers.DecimalField(source="product.current_price", max_digits=10, decimal_places=2)
    product_image = serializers.ImageField(source="product.main_image")

    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id',
            'product_id',
            'product_title',
            'product_price',
            'product_image',
            'quantity',
            'subtotal'
        ]

    def get_subtotal(self, obj):
        return obj.subtotal()


class CartDetailSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()
    # tax = serializers.SerializerMethodField()
    shipping = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'id',
            'items',
            'subtotal',
            'shipping',
            # 'tax',
            'discount',
            'total',
        ]

    def get_subtotal(self, obj):
        return obj.subtotal()

    def get_shipping(self, obj):
        return obj.shipping_cost()

    # def get_tax(self, obj):
    #     return obj.tax()

    def get_discount(self, obj):
        return obj.discount()

    def get_total(self, obj):
        return obj.total()
    
    
class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']



class UpdateQuantitySerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    
    
class DeleteItemFromCartSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()

class CartAndWatchlistCountSerializer(serializers.Serializer):
    item_count = serializers.IntegerField()
    watchlist_count = serializers.IntegerField()
    
    


class AddToCartCountResponseSerializer(serializers.Serializer):
    items_added = serializers.IntegerField()
    
    
    
class ShippingInfoSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    address = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    phone = serializers.CharField()
    alt_phone = serializers.CharField(allow_blank=True, required=False)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    

class ProductColorSerializer(serializers.Serializer):
    name = serializers.CharField()
    hex = serializers.CharField()

class ProductDetailSerializer(serializers.Serializer):
    tab = serializers.ChoiceField(choices=["description", "details", "shipping"])
    content = serializers.CharField()

class ProductImportSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField()
    original_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = serializers.IntegerField()
    rating = serializers.FloatField()
    category = serializers.ListField(child=serializers.CharField())
    sizes = serializers.ListField(child=serializers.CharField())
    colors = ProductColorSerializer(many=True)
    details = ProductDetailSerializer(many=True)

    def create(self, validated_data):
        from decimal import Decimal

        category_names = validated_data.pop('category')
        size_list = validated_data.pop('sizes')
        color_list = validated_data.pop('colors')
        details_list = validated_data.pop('details')

        # Handle categories
        product = Product.objects.create(
            title=validated_data['title'],
            description=validated_data['description'],
            original_price=validated_data['original_price'],
            discount_percent=validated_data['discount_percent'],
            rating=validated_data['rating'],
            display_product = False
        )
        for cat_name in category_names:
            category_obj, _ = Category.objects.get_or_create(name=cat_name)
            product.category.add(category_obj)

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





class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'description']


class ProductDetailColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductColor
        fields = ['color_name', 'hex_code']


class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ['size_label']


class ProductDetailByIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDetail
        fields = ['tab', 'title', 'content']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text']
        
        
class RelatedProductSerializer(serializers.ModelSerializer):
    product_image = serializers.SerializerMethodField() 
    class Meta:
        model = Product
        fields = ['id','title', 'product_image','current_price',]
        
    def get_product_image(self, obj):
        request = self.context.get('request')
        if obj.main_image and hasattr(obj.main_image, 'url'):
            return request.build_absolute_uri(obj.main_image.url)
        return None


class ProductDetailFullSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True)
    colors = ProductDetailColorSerializer(many=True)
    sizes = ProductSizeSerializer(many=True)
    details = ProductDetailByIdSerializer(many=True)
    images = ProductImageSerializer(many=True)
    related_products = serializers.SerializerMethodField()
    watchlisted = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'product_number', 'title', 'description', 'badge', 'main_image',
            'current_price', 'original_price', 'discount_percent',
            'rating', 'reviews_count', 'category', 'colors', 'sizes',
            'details', 'images', 'related_products', 'watchlisted', 'created_at'
        ]
        
    def get_related_products(self, obj):
        return RelatedProductSerializer(
            Product.objects.filter(
                category__in=obj.category.all()
            )
            .exclude(id=obj.id)
            .distinct()[:8],
            many=True,
            context=self.context
        ).data
        
    def get_watchlisted(self, obj):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            return WatchList.objects.filter(user=request.user, product=obj).exists()
        return False


# FOR RIDER

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
    
    
    
