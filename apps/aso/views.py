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
from apps.aso.BBL.Commands.Cart.AddToCart import AddToCartCommand
from apps.aso.BBL.Commands.Cart.MoveAllToCart import MoveAllToCartCommand
from apps.aso.BBL.Commands.Cart.RemoveCartItem import RemoveCartItemCommand
from apps.aso.BBL.Commands.Cart.UpdateCartDesc import UpdateCartDescCommand
from apps.aso.BBL.Commands.Cart.UpdateCartQuantity import UpdateCartQuantityCommand
from apps.aso.BBL.Commands.Cart.UpdateCartState import UpdateCartStateCommand
from apps.aso.BBL.Commands.Watchlist.RemoveAllWatchlist import RemoveAllWatchlistCommand
from apps.aso.BBL.Commands.Cart.ReorderItems import ReorderItemsCommand
from apps.aso.BBL.Commands.Watchlist.ToggleWatchlist import ToggleWatchlistCommand
from apps.aso.BBL.Commands.Cart.PlaceOrder import PlaceOrderCommand
from apps.aso.BBL.Queries.Cart.GetCartDetails import GetCartDetailQuery
from apps.aso.BBL.Queries.Cart.PaystackConfirm import PaystackConfirmQuery
from apps.aso.BBL.Queries.Watchlist.GetWatchlistProducts import GetWatchlistProductsQuery
from apps.aso.BBL.Queries.Watchlist.OrderDetails import OrderDetailQuery
from apps.aso.BBL.Queries.Order.UserOrderList import UserOrderListQuery
from apps.users.models import UserVerification
from utils.permissions import IsCustomerPermission, IsRiderPermission
from .models import *
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
    permission_classes = [IsAuthenticated, IsCustomerPermission]

    def get(self, request):
        result = UserOrderListQuery.query(self.request.user)
        return Response(result.to_dict(), status=result.status_code)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    
class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    # swagger_schema = TaggedAutoSchema

    def get(self, request, pk):
        result = OrderDetailQuery.query(self.request.user, pk)
        return Response(result.to_dict(), status=result.status_code)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    
class ReorderItemsView(generics.GenericAPIView):
    serializer_class = AddToCartCountResponseSerializer
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    # swagger_schema = TaggedAutoSchema

    def post(self, request):
        order_id = request.GET.get("order_id")
        result = ReorderItemsCommand.execute(request.user, order_id)
        return Response(result.to_dict(), status=result.status_code)
    


class WatchlistProductsView(generics.ListAPIView):
    serializer_class = WatchlistProductSerializer
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    # swagger_schema = TaggedAutoSchema

    def get(self, request):
        result = GetWatchlistProductsQuery.query(request.user)
        return Response(result.to_dict(), status=result.status_code)
    

class ToggleWatchlistView(APIView):
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    # swagger_schema = TaggedAutoSchema
    def put(self, request, product_id):
        result = ToggleWatchlistCommand.execute(request.user, product_id)
        return Response(result.to_dict(), status=result.status_code)
        

class RemoveAllWatchlistView(APIView):
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    # swagger_schema = TaggedAutoSchema

    def delete(self, request):
        result = RemoveAllWatchlistCommand.execute(request.user)
        return Response(result.to_dict(), status=result.status_code)
    
class MoveAllToCartView(generics.GenericAPIView):
    serializer_class = AddToCartCountResponseSerializer
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    # swagger_schema = TaggedAutoSchema

    def post(self, request):
        result = MoveAllToCartCommand.execute(request.user)
        return Response(result.to_dict(), status=result.status_code)
    
    
class AddToCartView(generics.GenericAPIView):
    serializer_class = AddToCartCountResponseSerializer
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    # swagger_schema = TaggedAutoSchema

    def post(self, request):
        result = AddToCartCommand.execute(
            user=request.user,
            product_id=request.GET.get("product_id"),
            quantity=request.GET.get("quantity"),
            desc=request.data.get("desc", "{}")
        )
        return Response(result.to_dict(), status=result.status_code)
    
class CartDetailAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    serializer_class = CartDetailSerializer
    # swagger_schema = TaggedAutoSchema

    def get(self, request, *args, **kwargs):
        result = GetCartDetailQuery.query(request.user)
        return Response(result.to_dict(), status=result.status_code)

        

class UpdateCartQuantityView(APIView):
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    serializer_class = UpdateQuantitySerializer
    # swagger_schema = TaggedAutoSchema 
    
    def patch(self, request):
        serializer = UpdateQuantitySerializer(data=request.data)
        result = UpdateCartQuantityCommand.execute(request.user, serializer)
        return Response(result.to_dict(), status=result.status_code)
    
    
class UpdateCartDescView(APIView):
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    serializer_class = UpdateDescSerializer
    # swagger_schema = TaggedAutoSchema 
    
    def patch(self, request):
        serializer = UpdateDescSerializer(data=request.data)
        result = UpdateCartDescCommand.execute(request.user, serializer)
        return Response(result.to_dict(), status=result.status_code)


class RemoveCartItemView(APIView):
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    serializer_class = DeleteItemFromCartSerializer
    # swagger_schema = TaggedAutoSchema
    
    def delete(self, request):
        serializer = DeleteItemFromCartSerializer(data=request.data)
        result = RemoveCartItemCommand.execute(request.user, serializer)
        return Response(result.to_dict(), status=result.status_code)

class UpdateCartStateView(APIView):
    permission_classes = [IsAuthenticated, IsCustomerPermission]

    def post(self, request):
        state = request.data.get("state")

        result = UpdateCartStateCommand.execute(request.user, state)
        return Response(result.to_dict(), status=result.status_code)
    
   
class PlaceOrderView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShippingInfoSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data.get("shipping_info"))
        serializer.is_valid(raise_exception=True)
        shipping_data = serializer.validated_data

        result = PlaceOrderCommand.execute(request, shipping_data)
        return Response(result.to_dict(), status=result.status_code)
        
        
class PaystackConfirmSubscriptionView(APIView):
    def get(self, request, reference, *args, **kwargs):
        return PaystackConfirmQuery.execute(reference)


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(display_product = True, is_deleted = False)
    authentication_classes = [OptionalJWTAuthentication]
    permission_classes = [AllowAny]
    serializer_class = WatchlistProductSerializer
    # swagger_schema = TaggedAutoSchema
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
    queryset = Product.objects.filter(display_product=True, is_deleted = False)
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
    permission_classes = [IsAuthenticated, IsCustomerPermission]
    serializer_class = OrderDetailSerializer
    # swagger_schema = TaggedAutoSchema
    
    def get(self, request):
        cart_count = 0
        watchlist_count = 0

        try:
            cart = Cart.objects.get(user=request.user, is_deleted = False)
            cart_count = cart.items.count()
        except Cart.DoesNotExist:
            pass

        watchlist_count = WatchList.objects.filter(user=request.user, is_deleted = False).count()

        serializer = CartAndWatchlistCountSerializer({
            'item_count': cart_count,
            'watchlist_count': watchlist_count
        })

        return Response(serializer.data)
    
    
class LookUpView(APIView):
    serializer_class = LookUpsSerializer

    # @swagger_auto_schema(tags=["Categories"])
    # swagger_schema = TaggedAutoSchema
    def get(self, request):
        lookups = LookUp.objects.filter(is_deleted = False)
        serializer = self.serializer_class(lookups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    

class RiderDashboardView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsRiderPermission]
    serializer_class = RiderDashboardSerializer

    def get(self, request, *args, **kwargs):
        rider = request.user

        profile_data = {
            "name": f"{rider.first_name} {rider.last_name}",
            "rider_id": rider.rider_number,
            "deliveries_count": Order.objects.filter(
                dispatcher=rider,
                delivery_date__isnull=False, is_deleted = False
            ).count()
        }

        # Get query param for product_id filter
        search = request.query_params.get("search")
        recent_orders = Order.objects.filter(
            dispatcher=rider,
            delivery_date__isnull=False, is_deleted = False
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
    permission_classes = [IsAuthenticated, IsRiderPermission]

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order_number = serializer.validated_data["order_number"]

        # Validate order existence
        try:
            order = Order.objects.get(order_number=order_number, is_deleted = False)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if OrderTracking.objects.filter(order=order, status__in=["delivered", "cancelled"], is_deleted = False).exists():
            return Response(
                {"error": "Order already delivered or cancelled, OTP not required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not OrderTracking.objects.filter(order=order, status="in_transit", is_deleted = False).exists():
            return Response(
                {"error": "Order is not currently in transit, OTP cannot be sent."},
                status=status.HTTP_400_BAD_REQUEST
            )


        user = order.user

        # Create or update verification
        verification, _ = UserVerification.objects.get_or_create(user=user, is_deleted = False)
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
    permission_classes = [IsAuthenticated, IsRiderPermission]
    
    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_number = serializer.validated_data["order_number"]
        otp = serializer.validated_data["otp"]

        # Validate order existence
        try:
            order = Order.objects.get(order_number=order_number, is_deleted = False)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        # Validate verification record
        try:
            verification = UserVerification.objects.get(user=order.user, is_deleted = False)
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
                "image": request.build_absolute_uri(item.product.main_image.url) if item.product.main_image else None,
                "desc": item.desc
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
                "other_info": order.other_info,
                "items": order_items_data
            }
        }
        
        print(order_data)

        return Response(order_data, status=status.HTTP_200_OK)



class RiderOderDetailsView(generics.GenericAPIView):
    serializer_class = RiderOderDetailsSerializer
    permission_classes = [IsAuthenticated, IsRiderPermission]
    
    def post(self, request, *args, **kwargs):        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_number = serializer.validated_data["order_number"]

        # Validate order existence
        try:
            order = Order.objects.get(order_number=order_number, is_deleted = False)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

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
                "image": request.build_absolute_uri(item.product.main_image.url) if item.product.main_image else None,
                "desc": item.desc
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
                "other_info": order.other_info,
                "items": order_items_data
            }
        }
        
        print(order_data)

        return Response(order_data, status=status.HTTP_200_OK)

    
class MarkOrderAsDeliveredView(generics.GenericAPIView):
    serializer_class = MarkOrderAsDeliveredSerializer
    permission_classes = [IsAuthenticated, IsRiderPermission]
    
    def post(self, request, *args, **kwargs):
        rider = request.user
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_number = serializer.validated_data["order_number"]
        delivery_notes = serializer.validated_data["delivery_notes"]
        stars = serializer.validated_data.get("stars")
        
        if not stars or not str(stars).isdigit() or not (1 <= int(stars) <= 5):
            return Response({"error": "Please provide a valid star rating between 1 and 5"}, status=400)

        # Find the order
        try:
            order = Order.objects.get(order_number=order_number, is_deleted = False)
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
    
class DeliveryFeeAPIView(APIView):
    authentication_classes = [OptionalJWTAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"delivery_fees": delivery_fees})