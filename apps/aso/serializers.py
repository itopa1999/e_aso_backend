from rest_framework import serializers

from .models import Cart, CartItem, LookUp, Order, OrderItem, OrderTracking, PaymentDetail, Product, ProductColor, ProductDetail, ProductImage, ProductSize, ShippingAddress, WatchList

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.title')
    product_image = serializers.SerializerMethodField()
    product_id = serializers.IntegerField(source = 'product.id')
    class Meta:
        model = OrderItem
        fields = ['product_name', 'product_id', 'price', 'quantity', 'desc', 'product_image']
        
    def get_product_image(self, obj):
        request = self.context.get('request')
        if obj.product.main_image and hasattr(obj.product.main_image, 'url'):
            return request.build_absolute_uri(obj.product.main_image.url)
        return None
    
        
class OrderTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTracking
        fields = ['status', 'date', 'description', 'completed']
        
        
class OrderTrackingDetailsSerializer(serializers.ModelSerializer):
    tracking = OrderTrackingSerializer(source='tracking_events', many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'tracking']
        
        
        
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
            'id', 'order_number', 'created_at', 'order_status', 'other_info',
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
            'id', 'order_number', 'created_at', 'subtotal', 'shipping_fee', 'discount', 'other_info',
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
    cart_added = serializers.SerializerMethodField()

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
            'watchlisted',
            'cart_added',
        ]
    
    def get_current_price(self, obj):
        return float(obj.current_price or 0)
    
    def get_short_description(self, obj):
        return obj.description[:80] + "..." if len(obj.description) > 80 else obj.description
    
    def get_watchlisted(self, obj):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            return WatchList.objects.filter(user=request.user, product=obj, is_deleted = False).exists()
        return False
    
    def get_cart_added(self, obj):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            return CartItem.objects.filter(
                cart__user=request.user,
                product=obj,
                is_deleted=False
            ).exists()
        return False

    

class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id")
    product_title = serializers.CharField(source="product.title")
    product_price = serializers.DecimalField(source="product.current_price", max_digits=10, decimal_places=2)
    product_image = serializers.SerializerMethodField()
    product_colors = serializers.SerializerMethodField()
    product_sizes = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id',
            'product_id',
            'product_title',
            'product_price',
            'product_image',
            'product_colors',
            'product_sizes',
            'quantity',
            'subtotal',
            "desc"
        ]
        
    def get_product_colors(self, obj):
        """Return all available colors for the product as a list of dicts."""
        return [
            {
                "name": color.color_name,
            }
            for color in obj.product.colors.all()
        ]

    def get_product_sizes(self, obj):
        """Return all available sizes for the product as a list of size labels."""
        return [size.size_label for size in obj.product.sizes.all()]

    def get_subtotal(self, obj):
        return obj.subtotal()
    
    def get_product_image(self, obj):
        request = self.context.get('request')
        
        if obj.product.main_image and hasattr(obj.product.main_image, 'url'):
            return request.build_absolute_uri(obj.product.main_image.url)
        return None


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

    
    
class LookUpsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LookUp
        fields = ['name', 'category']



class UpdateQuantitySerializer(serializers.Serializer):
    item_id = serializers.IntegerField(required = True)
    quantity = serializers.IntegerField(min_value=1)
    
class UpdateDescSerializer(serializers.Serializer):
    item_id = serializers.IntegerField(required = True)
    desc = serializers.JSONField(required = True)
    
    
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
    otherInfo = serializers.CharField(required=False)





class LookUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = LookUp
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
    category = LookUpSerializer(many=True)
    colors = ProductDetailColorSerializer(many=True)
    sizes = ProductSizeSerializer(many=True)
    details = ProductDetailByIdSerializer(many=True)
    images = ProductImageSerializer(many=True)
    related_products = serializers.SerializerMethodField()
    watchlisted = serializers.SerializerMethodField()
    cart_added = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'product_number', 'title', 'description', 'badge', 'main_image',
            'current_price', 'original_price', 'discount_percent',
            'rating', 'reviews_count', 'category', 'colors', 'sizes',
            'details', 'images', 'related_products', 'watchlisted', 'created_at', 'cart_added'
        ]
        
    def get_related_products(self, obj):
        return RelatedProductSerializer(
            Product.objects.filter(
                category__in=obj.category.all(), is_deleted = False
            )
            .exclude(id=obj.id)
            .distinct()[:8],
            many=True,
            context=self.context
        ).data
        
    def get_watchlisted(self, obj):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            return WatchList.objects.filter(user=request.user, product=obj, is_deleted = False).exists()
        return False
        
    def get_cart_added(self, obj):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            return CartItem.objects.filter(
                cart__user=request.user,
                product=obj,
                is_deleted=False
            ).exists()
        return False


    
