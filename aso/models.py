from django.db import models
from administrator.models import User
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

from aso.deliveryFee import DELIVERY_FEES
# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    Badge = [
        ('New', 'New'),
        ('Best Seller', 'Best Seller'),
        ('Limited', 'Limited')
    ]
    product_number = models.CharField(max_length=100, null=True, blank=True, editable=False)
    category = models.ManyToManyField(Category, related_name="product")

    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    
    current_price = models.DecimalField(max_digits=10, decimal_places=2, db_index=True, null=True, blank=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.PositiveIntegerField(null=True, blank=True)
    
    rating = models.FloatField(default=0.0)
    reviews_count = models.PositiveIntegerField(default=0)

    badge = models.CharField(max_length=50, blank=True, choices=Badge, default="New")
    main_image = models.ImageField(upload_to='products/main/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    display_product = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.product_number:
            last_product = Product.objects.order_by('-id').first()
            next_id = 1 if not last_product else last_product.id + 1
            self.product_number = f"#AO-P-{str(next_id).zfill(4)}"
            
            
        if self.discount_percent:
            if self.discount_percent:
                # Ensure consistent Decimal types
                discount = Decimal(self.discount_percent) / Decimal('100')
                self.current_price = self.original_price - (self.original_price * discount)
            else:
                self.current_price = self.original_price
        else:
            # No discount: set both prices the same
            if self.original_price:
                self.current_price = self.original_price
            else:
                self.original_price = self.current_price

        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['current_price']),
        ]

    def __str__(self):
        return self.title
    
    @property
    def category_names(self):
        return ", ".join([cat.name for cat in self.category.all()])


class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='colors')
    color_name = models.CharField(max_length=100)
    hex_code = models.CharField(max_length=7, null=True, blank=True)
    
    class Meta:
        unique_together = ('product', 'color_name')

    def __str__(self):
        return f"{self.product.title} - {self.color_name}"
    


class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')
    size_label = models.CharField(max_length=50)  # e.g. 5, 6, 7, 8 yards
    
    class Meta:
        unique_together = ('product', 'size_label')

    def __str__(self):
        return f"{self.product.title} - Size {self.size_label}"
    
    

class ProductDetail(models.Model):
    TAB_CHOICES = [
        ('description', 'Description'),
        ('details', 'Product Details'),
        ('shipping', 'Shipping & Returns')
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='details')
    tab = models.CharField(max_length=50, choices=TAB_CHOICES)
    title = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return f"{self.product.title} - {self.tab} - {self.title}"
    
    
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=255, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['product']),
        ]
        
    def __str__(self):
        return f"{self.product.title}"
    
    
class WatchList(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='watchlist_product')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist_user')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']

    def __str__(self):
        return f"watch_{self.product.title}"
    
    
    
    
User = get_user_model()

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    state = models.CharField(max_length=100, blank=True, null=True)

    def subtotal(self):
        return sum(item.subtotal() for item in self.items.all())

    def shipping_cost(self):
        return Decimal(DELIVERY_FEES.get(self.state, 0))  # static for now

    # def tax(self):
    #     return self.subtotal() * Decimal("0.05")  # 5% tax example

    def discount(self):
        return Decimal("0.00")  # set by logic/rules

    def total(self):
        return self.subtotal() + self.shipping_cost() - self.discount()

    def __str__(self):
        return f"{self.user.first_name}'s Cart"

    class Meta:
        indexes = [models.Index(fields=["user"])]

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    desc = models.JSONField(null=True, blank=True)

    def subtotal(self):
        return self.product.current_price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"

    class Meta:
        unique_together = ('cart', 'product')
        indexes = [
            models.Index(fields=['cart']),
            models.Index(fields=['product']),
        ]
        
        

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True, db_index=True, null=True, blank=True, editable=False)

    other_info = models.TextField(null=True, blank=True)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    tracking_number = models.CharField(max_length=50, null=True, blank=True, editable=False)
    carrier = models.CharField(max_length=100, blank=True, default="Aso Oke Express")
    
    dispatcher = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='rider')
    delivery_date = models.DateField(null=True, blank=True)
    
    estimated_delivery_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    
    def save(self, *args, **kwargs):
        if not self.order_number:
            last_order = Order.objects.order_by('-id').first()
            next_id = 1 if not last_order else last_order.id + 1
            self.order_number = f"#AO-OD-{str(next_id).zfill(4)}"

        if not self.tracking_number:
            last_order_tracking = Order.objects.order_by('-id').first()
            next_id = 1 if not last_order_tracking else last_order_tracking.id + 1
            self.tracking_number = f"#AO-OT-{str(next_id).zfill(4)}"
            
        if self.estimated_delivery_date is None:
            self.estimated_delivery_date = (self.created_at or timezone.now()).date() + timedelta(days=7)
            
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Order #{self.order_number} by {self.user.username}"

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['order_number']), models.Index(fields=['user'])]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot of product price at purchase
    desc = models.JSONField(null=True, blank=True)

    def total_price(self):
        return self.price * self.quantity
    
    class Meta:
        unique_together = ('order', 'product')
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product']),
        ]

    def __str__(self):
        return f"{self.product.title} x{self.quantity}"


class ShippingAddress(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping_address')

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    alt_phone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.address}"


class PaymentDetail(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment_detail')
    method = models.CharField(max_length=50)  # e.g. 'Mastercard', 'Bank Transfer'

    def __str__(self):
        return f"{self.method}"


class OrderTracking(models.Model):
    STATUS_CHOICES = [
        ('placed', 'Order Placed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking_events')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='placed')
    date = models.DateTimeField()
    description = models.TextField()
    completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('status', 'order')
        ordering = ['-id']

    def __str__(self):
        return f"{self.status} - {self.order.order_number}"
    
    
    
class OrderFeedBack(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='feedback')
    stars = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for Order {self.order.order_number} - {self.stars} Stars"
    
    
    
class OrderReturn(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='return_product')
    reason = models.CharField(max_length=500)
    message = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"return request for Order {self.order.order_number}"
    