from django.shortcuts import redirect, render
import requests as req
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.core.mail import send_mail
from administrator.models import UserVerification
from .models import *
from administrator.swagger import TaggedAutoSchema
from .serializers import *
from .deliveryFee import delivery_fees
from .paystack import *
from django.db.models import Q
from rest_framework.exceptions import AuthenticationFailed
import random, textwrap
# Create your views here.

class OptionalJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None  # No token → AnonymousUser

        try:
            return super().authenticate(request)
        except AuthenticationFailed:
            # Invalid/expired token → Ignore, treat as anonymous
            return None

class UserOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    swagger_schema = TaggedAutoSchema

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items', 'tracking_events')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    
class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]
    swagger_schema = TaggedAutoSchema

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    
class ReorderItemsView(generics.GenericAPIView):
    serializer_class = AddToCartCountResponseSerializer
    permission_classes = [IsAuthenticated]
    swagger_schema = TaggedAutoSchema

    def post(self, request):
        order_id = request.GET.get("order_id")
        user = request.user

        if not order_id:
            return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id, user=user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        cart, _ = Cart.objects.get_or_create(user=user)
        items_added = 0

        for item in order.items.all():
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=item.product,
                defaults={"quantity": item.quantity}
            )
            if created:
                items_added += 1

        serializer = AddToCartCountResponseSerializer({"items_added": items_added})
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class WatchlistProductsView(generics.ListAPIView):
    serializer_class = WatchlistProductSerializer
    permission_classes = [IsAuthenticated]
    swagger_schema = TaggedAutoSchema

    def get_queryset(self):
        user = self.request.user
        return Product.objects.filter(watchlist_product__user=user)
    

class ToggleWatchlistView(APIView):
    permission_classes = [IsAuthenticated]
    swagger_schema = TaggedAutoSchema
    def put(self, request, product_id):
        user = request.user
        watchlist_item, created = WatchList.objects.get_or_create(user=user, product_id=product_id)

        if not created:
            # Already exists, so remove it
            watchlist_item.delete()
            return Response({"watchlisted": False}, status=status.HTTP_200_OK)
        else:
            # Newly added
            return Response({"watchlisted": True}, status=status.HTTP_200_OK)
        
        

class RemoveAllWatchlistView(APIView):
    permission_classes = [IsAuthenticated]
    swagger_schema = TaggedAutoSchema

    def delete(self, request):
        user = request.user
        deleted_count, _ = WatchList.objects.filter(user=user).delete()
        return Response({"message": f"{deleted_count} items removed."}, status=status.HTTP_200_OK)
    
    
class MoveAllToCartView(generics.GenericAPIView):
    serializer_class = AddToCartCountResponseSerializer
    permission_classes = [IsAuthenticated]
    swagger_schema = TaggedAutoSchema

    def post(self, request):
        user = request.user
        watchlist_items = WatchList.objects.filter(user=user)
        if not watchlist_items.exists():
            return Response({"items_moved": 0}, status=status.HTTP_200_OK)

        cart, _ = Cart.objects.get_or_create(user=user)
        items_moved = 0

        for item in watchlist_items:
            product = item.product
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': 1}
            )
            if created:
                items_moved += 1

        serializer = AddToCartCountResponseSerializer({"items_added": items_moved})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class AddToCartView(generics.GenericAPIView):
    serializer_class = AddToCartCountResponseSerializer
    permission_classes = [IsAuthenticated]
    swagger_schema = TaggedAutoSchema

    def post(self, request):
        product_id = request.GET.get("product_id")
        quantity = request.GET.get("quantity", 1)

        if not product_id:
            return Response({"error": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        items_moved = 0
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": int(quantity)}
        )

        if created:
            items_moved += 1

        serializer = AddToCartCountResponseSerializer({"items_added": items_moved})
        return Response(serializer.data, status=status.HTTP_200_OK)
        


class CartDetailAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartDetailSerializer
    swagger_schema = TaggedAutoSchema

    def get(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

        

class UpdateCartQuantityView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateQuantitySerializer
    swagger_schema = TaggedAutoSchema 
    
    def patch(self, request):
        serializer = UpdateQuantitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        item_id = serializer.validated_data["item_id"]
        quantity = serializer.validated_data["quantity"]
        
        print(item_id, quantity)

        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
            item.quantity = quantity
            item.save()
            return Response({'message:': 'Ok'}, status=status.HTTP_200_OK)

        except CartItem.DoesNotExist:
            return Response({"detail": "Item not found."}, status=status.HTTP_404_NOT_FOUND)
    


class RemoveCartItemView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DeleteItemFromCartSerializer
    swagger_schema = TaggedAutoSchema
    
    def delete(self, request):
        serializer = DeleteItemFromCartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        item_id = serializer.validated_data["item_id"]

        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
            item.delete()
            return Response({'message:': 'Ok'}, status=status.HTTP_200_OK)

        except CartItem.DoesNotExist:
            return Response({"error": "Item not found."}, status=status.HTTP_404_NOT_FOUND)
    

class UpdateCartStateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        state = request.data.get("state")

        try:
            cart = request.user.cart
        except Cart.DoesNotExist:
            pass
        cart.state = state
        cart.save()
        return Response(status=200)
    
    
class PlaceOrderView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShippingInfoSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data.get("shipping_info"))
        serializer.is_valid(raise_exception=True)
        
        shipping_data = serializer.validated_data

        try:
            cart = request.user.cart
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found."}, status=status.HTTP_400_BAD_REQUEST)

        expected_total = cart.total()
        user_total = Decimal(shipping_data["total"])

        if expected_total != user_total:
            return Response({
                "error": f"Total mismatch. Expected ₦{expected_total}, got ₦{user_total}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Print shipping info
        print("Received Order Shipping Info:")
        for key, value in shipping_data.items():
            print(f"{key}: {value}")
            
        checkout_link = initiate(request, user=request.user, cart_id=cart.id, data=shipping_data)

        if not checkout_link:
            return Response({"error": "Payment initialization failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "message": "Order initialized successfully.",
            "checkout_url": checkout_link,
        }, status=status.HTTP_200_OK) 
        
        
class PaystackConfirmSubscriptionView(APIView):
    def get(self, request, reference, *args, **kwargs):
        if not reference:
            return Response({"error": "No reference provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        result = validate(reference)

        if result.get("success"):
            order = result.get("order")
            return redirect(
                f"{settings.BASE_URL}/order-success.html"
                f"?order_id={order['id']}"
                f"&order_number={order['order_number']}"
                f"&amount={order['amount']}"
                f"&created_at={order['created_at']}"
            )
        else:
            return Response({"error": result["error"]}, status=status.HTTP_400_BAD_REQUEST)

    
    
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(display_product = True)
    authentication_classes = [OptionalJWTAuthentication]
    permission_classes = [AllowAny]
    serializer_class = WatchlistProductSerializer
    swagger_schema = TaggedAutoSchema
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['badge']
    ordering_fields = ['current_price', 'rating', 'created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        max_price = self.request.query_params.get('max_price')
        min_price = self.request.query_params.get('min_price')
        rating = self.request.query_params.get('rating')
        search = self.request.query_params.get('search')
        cat = self.request.query_params.get('category')
        
        if min_price:
            queryset = queryset.filter(current_price__gte=min_price)

        if max_price:
            queryset = queryset.filter(current_price__lte=max_price)

        if rating:
            queryset = queryset.filter(rating=rating)

        if cat:
            queryset = queryset.filter(category__name__icontains=cat)

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(product_number__icontains=search) |
                Q(category__name__icontains=search)
            )

        return queryset
        

    
    def get_serializer_context(self):
        return {"request": self.request}
    
    
    
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(display_product=True)
    serializer_class = ProductDetailFullSerializer
    authentication_classes = [OptionalJWTAuthentication]
    permission_classes = [AllowAny]
    lookup_field = 'id'
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def retrieve(self, request, *args, **kwargs):
        # Get the product
        instance = self.get_object()

        # Increment reviews_count
        instance.reviews_count = (instance.reviews_count or 0) + 1
        instance.save(update_fields=['reviews_count'])

        # Serialize and return response
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    

class CartAndWatchlistCountView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderDetailSerializer
    swagger_schema = TaggedAutoSchema
    
    def get(self, request):
        cart_count = 0
        watchlist_count = 0

        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = cart.items.count()
        except Cart.DoesNotExist:
            pass

        watchlist_count = WatchList.objects.filter(user=request.user).count()

        serializer = CartAndWatchlistCountSerializer({
            'item_count': cart_count,
            'watchlist_count': watchlist_count
        })

        return Response(serializer.data)
    
    
class CategoriesView(generics.ListAPIView):
    serializer_class = CategoriesSerializer
    swagger_schema = TaggedAutoSchema

    def get_queryset(self):
        return Category.objects.all()
    
    
    
class ProductBulkImportView(APIView):
    def post(self, request):
        if not isinstance(request.data, list):
            return Response({'error': 'Data must be a list of products'}, status=status.HTTP_400_BAD_REQUEST)

        created_count = 0
        errors = []

        for idx, item in enumerate(request.data):
            serializer = ProductImportSerializer(data=item)
            if serializer.is_valid():
                serializer.save()
                created_count += 1
            else:
                errors.append({
                    "index": idx,
                    "errors": serializer.errors
                })

        return Response({
            "message": "Import finished",
            "products_created": created_count,
            "errors": errors
        }, status=status.HTTP_200_OK)
        

class RiderDashboardView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RiderDashboardSerializer

    def get(self, request, *args, **kwargs):
        rider = request.user

        # Only allow if user is a rider
        if not rider.groups.filter(name__iexact='rider').exists():
            return Response({"error": "Not authorized"}, status=401)

        profile_data = {
            "name": f"{rider.first_name} {rider.last_name}",
            "rider_id": rider.rider_number,
            "deliveries_count": Order.objects.filter(
                dispatcher=rider,
                delivery_date__isnull=False
            ).count()
        }

        # Get query param for product_id filter
        search = request.query_params.get("search")
        recent_orders = Order.objects.filter(
            dispatcher=rider,
            delivery_date__isnull=False
        )
        if search:
            recent_orders = recent_orders.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(order_number__icontains=search) |
                Q(total__icontains=search)
                )

        recent_orders = recent_orders.order_by('-delivery_date')

        # Paginate
        page = self.paginate_queryset(recent_orders)
        if page is not None:
            return self.get_paginated_response({
                "profile": profile_data,
                "recent_deliveries": RiderDashboardSerializer({
                    "profile": profile_data,
                    "recent_deliveries": page
                }).data["recent_deliveries"]
            })

        serializer = self.get_serializer({
            "profile": profile_data,
            "recent_deliveries": recent_orders
        })
        return Response(serializer.data)


class SendOtpView(generics.GenericAPIView):
    serializer_class = SendOtpSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        rider = request.user

        # Only allow if user is a rider
        if not rider.groups.filter(name__iexact='rider').exists():
            return Response({"error": "Not authorized"}, status=401)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order_number = serializer.validated_data["order_number"]

        # Validate order existence
        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if OrderTracking.objects.filter(order=order, status__in=["delivered", "cancelled"]).exists():
            return Response(
                {"error": "Order already delivered or cancelled, OTP not required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not OrderTracking.objects.filter(order=order, status="in_transit").exists():
            return Response(
                {"error": "Order is not currently in transit, OTP cannot be sent."},
                status=status.HTTP_400_BAD_REQUEST
            )


        user = order.user

        # Create or update verification
        verification, _ = UserVerification.objects.get_or_create(user=user)
        verification.token = str(random.randint(100000, 999999))
        verification.created_at = timezone.now()
        verification.is_verified = False
        verification.save()

        # Send OTP via email
        send_mail(
            subject="Your Delivery OTP",
            message = textwrap.dedent(f"""
                Dear {user.first_name or "Valued Customer"},

                Your **One-Time Password (OTP)** is: **{verification.token}**  

                This OTP will expire in **10 minutes** for your security.  
                If you did not request this code, please ignore this message.

                Need help? Contact us:  
                📞 +234 1 700 0000  
                ✉️ support@aso-okemarketplace.ng  

                Preserving Nigeria’s textile heritage,  
                **The Aso Oke & Aso Ofi Marketplace Team**
            """),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False
        )

        return Response({"message": "OTP sent to customer's email"}, status=status.HTTP_200_OK)


class VerifyOtpView(generics.GenericAPIView):
    serializer_class = VerifyOtpSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        rider = request.user

        # Only allow if user is a rider
        if not rider.groups.filter(name__iexact='rider').exists():
            return Response({"error": "Not authorized"}, status=401)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_number = serializer.validated_data["order_number"]
        otp = serializer.validated_data["otp"]

        # Validate order existence
        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        # Validate verification record
        try:
            verification = UserVerification.objects.get(user=order.user)
        except UserVerification.DoesNotExist:
            return Response({"error": "No OTP found for this user"}, status=status.HTTP_400_BAD_REQUEST)

        # Check expiration
        if timezone.now() > verification.created_at + timezone.timedelta(minutes=10):
            return Response({"error": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST)

        # Check match
        if int(verification.token) != int(otp):
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        verification.is_verified = True
        verification.save()

        # Fetch shipping address
        shipping = getattr(order, 'shipping_address', None)

        # Fetch order items
        items = order.items.select_related('product').all()
        order_items_data = [
            {
                "product_id" : item.product.id,
                "product": item.product.title,
                "quantity": item.quantity,
                "price": f"₦{item.price:,.0f}",
                "total_price": f"₦{item.total_price():,.0f}",
                "image": request.build_absolute_uri(item.product.main_image.url) if item.product.main_image else None
            }
            for item in items
        ]

        # Prepare response data
        order_data = {
            "message": "OTP verified successfully",
            "order_details": {
                "order_id": order.order_number,
                "customer": f"{order.user.first_name} {order.user.last_name}" if order.user.last_name else "Not Set",
                "delivery_address": f"{shipping.address}, {shipping.city}, {shipping.state}" if shipping else "",
                "contact": shipping.phone if shipping.phone else shipping.alt_phone,
                "order_date": order.created_at.strftime("%b %d, %Y"),
                "total_amount": f"₦{order.total:,.0f}",
                "items": order_items_data
            }
        }

        return Response(order_data, status=status.HTTP_200_OK)
    
class MarkOrderAsDeliveredView(generics.GenericAPIView):
    serializer_class = MarkOrderAsDeliveredSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        rider = request.user

        # Only allow if user is a rider
        if not rider.groups.filter(name__iexact='rider').exists():
            return Response({"error": "Not authorized"}, status=401)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_number = serializer.validated_data["order_number"]
        delivery_notes = serializer.validated_data["delivery_notes"]
        stars = serializer.validated_data.get("stars")
        
        if not stars or not str(stars).isdigit() or not (1 <= int(stars) <= 5):
            return Response({"error": "Please provide a valid star rating between 1 and 5"}, status=400)

        # Find the order
        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        # Create tracking event
        tracking_event = OrderTracking.objects.create(
            order=order,
            status="delivered",
            date=timezone.now(),
            description=delivery_notes or "Order marked as delivered.",
            completed=True
        )
        
        OrderFeedBack.objects.update_or_create(
            order=order,
            defaults={
                "stars": int(stars),
                "comment": delivery_notes
            }
        )

        # Update order delivery date
        order.dispatcher = rider
        order.delivery_date = timezone.now()
        order.save()
        
        

        # Send email to customer
        send_mail(
            subject="Your Order Has Been Delivered",
            message = textwrap.dedent(f"""
                Dear {order.user.get_full_name() or "Valued Customer"},

                Your order **{order.order_number}** has been successfully delivered.  
                Thank you for shopping with us!

                Need help? Contact us:  
                📞 +234 1 700 0000  
                ✉️ support@aso-okemarketplace.ng  

                Preserving Nigeria’s textile heritage,  
                **The Aso Oke & Aso Ofi Marketplace Team**
            """),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[order.user.email],
            fail_silently=False,
        )
        

        return Response({
            "message": "Order marked as delivered successfully",
            "order_number": order.order_number
        })

    
    
    
    
class ActivateProductsAPIView(APIView):
    def post(self, request):
        products_to_update = Product.objects.filter(display_product=False)
        count = products_to_update.update(display_product=True)
        return Response({"message": f"{count} products activated."}, status=status.HTTP_200_OK)
    
    
class DeliveryFeeAPIView(APIView):
    authentication_classes = [OptionalJWTAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"delivery_fees": delivery_fees})