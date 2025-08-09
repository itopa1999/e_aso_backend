from django.shortcuts import redirect, render
import requests as req
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import *
from administrator.swagger import TaggedAutoSchema
from .serializers import *
from .deliveryFee import delivery_fees
from .paystack import *
from django.db.models import Q
from rest_framework.exceptions import AuthenticationFailed

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