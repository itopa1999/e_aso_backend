from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import *
from administrator.swagger import TaggedAutoSchema
from .serializers import *


from django.db.models import Q


# Create your views here.


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
            defaults={"quantity": 1}
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
    


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(display_product = True)
    permission_classes = [AllowAny]
    serializer_class = WatchlistProductSerializer
    swagger_schema = TaggedAutoSchema
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['badge']
    ordering_fields = ['current_price', 'rating']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        max_price = self.request.query_params.get('max_price')
        rating = self.request.query_params.get('rating')
        search = self.request.query_params.get('search')
        cat = self.request.query_params.get('category')

        if max_price:
            queryset = queryset.filter(current_price__lte=max_price)

        if rating:
            queryset = queryset.filter(rating=rating)
            
        if cat:
            queryset = queryset.filter(category__name=cat)

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(product_number__icontains=search)
            )
            
        return queryset
        

    
    def get_serializer_context(self):
        return {"request": self.request}
    
    

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