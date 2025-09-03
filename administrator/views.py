from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from datetime import datetime
from django.db.models import Q
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
import textwrap
from urllib.parse import urlencode

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from aso.models import OrderTracking, Product
from aso.serializers import OrderSerializer
from utils.magic_link import generate_magic_token, validate_magic_token


from .models import User, UserVerification
from .swagger import TaggedAutoSchema
from .serializers import *
# Create your views here. 


User = get_user_model()


class VerifyEmailView(APIView):
    swagger_schema = TaggedAutoSchema
    def get(self, request, uidb64, token, url_email):
        "pass"
    
    
class ResendVerificationEmailView(generics.GenericAPIView):
    serializer_class = ResendLinkSerializer
    swagger_schema = TaggedAutoSchema
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        is_login = serializer.validated_data['is_login']
        
        try:
            user = User.objects.get(email=email)
            
            if is_login:
                if not user.is_active:
                    return Response({"error": "Account inactive"}, status=400)
                uidb64 = urlsafe_base64_encode(force_bytes(user.id))
                token = generate_magic_token(email)

                verification_link = request.build_absolute_uri(
                    reverse('verify-magic-login', kwargs={'uidb64': uidb64, 'token': token, 'url_email': email})
                )
                
                send_mail(
                    subject="Your Magic Login Link",
                    message= textwrap.dedent(f"""
                        Dear {user.first_name or "Valued Customer" },

                        Here’s your secure **Magic Login Link** to access your Aso Oke & Aso Ofi Marketplace account:

                        {verification_link }

                        This link will expire in **10 minutes** for your security. If you did not request this login, please ignore this email.

                        Need help? Contact us:  
                        📞 +234 1 700 0000  
                        ✉️ support@aso-okemarketplace.ng  

                        Preserving Nigeria’s textile heritage,  
                        **The Aso Oke & Aso Ofi Marketplace Team** 
                        """),
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False
                )

                return Response({"message": "A new magic login link sent to email"}, status=200)

            if user.is_active:
                return Response({"error": "Email is already verified."}, status=status.HTTP_400_BAD_REQUEST)

            # Generate or reuse verification
            verification, _ = UserVerification.objects.get_or_create(user=user)
            verification.generate_token()
            verification.save()

            uidb64 = urlsafe_base64_encode(force_bytes(user.id))
            token = verification.token

            verification_link = request.build_absolute_uri(
                reverse('verify-email', kwargs={'uidb64': uidb64, 'token': token, 'url_email': email})
            )

            subject = "Verify Your Email - Aso Oke & Aso Ofi Marketplace"
            message = textwrap.dedent(f"""
                Dear {user.first_name or 'Valued Customer'},

                Welcome back to Aso Oke & Aso Ofi Marketplace!

                Please verify your email address by clicking the link below:

                {verification_link}

                This link will expire in 10 minutes. If you didn't request this email, you can safely ignore it.

                Thanks,
                The Aso Oke & Aso Ofi Marketplace Team
                """)

            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

            return Response({"message": "A new verification email has been sent."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

            

class SendMagicLinkView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    swagger_schema = TaggedAutoSchema
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            serializer = RegUserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            if serializer.is_valid():
                # Create user
                user = serializer.save()
                verification = UserVerification(user=user)
                verification.generate_token()
                verification.save()
                
                user.is_active = False
                user.save()
                
                token = verification.token
                uidb64 = urlsafe_base64_encode(force_bytes(user.id))
                verification_link = request.build_absolute_uri(
                    reverse('verify-email', kwargs={'uidb64': uidb64, 'token': token, 'url_email': email})
                )
                
                subject = "Verify Your Email - Aso Oke & Aso Ofi Marketplace"
        
                message = textwrap.dedent(f"""
                    Dear {user.first_name or 'Valued Customer'},

                    Welcome to Aso Oke & Aso Ofi Marketplace - Nigeria's premier destination for authentic traditional fabrics and textiles!

                    To complete your registration and access our exclusive marketplace, please verify your email address by clicking the link below:

                    {verification_link}

                    Explore our curated collections:
                    ✨ Handwoven Aso Oke fabrics
                    ✨ Premium Aso Ofi textiles
                    ✨ Traditional embroidery pieces
                    ✨ Custom tailoring services

                    Why verify your email?
                    ✅ Secure your account  
                    ✅ Receive order updates  
                    ✅ Access exclusive member discounts  
                    ✅ View and manage your order history 

                    The verification link will expire in 24 hours. If you didn't create an account with us, please ignore this email.

                    Need assistance? Contact our support team:
                    📞 +234 1 700 0000
                    ✉️ support@aso-okemarketplace.ng
                    📍 14 Traditional Weavers Road, Ilorin, Kwara State

                    Preserving Nigeria's textile heritage,
                    The Aso Oke & Aso Ofi Marketplace Team

                    Celebrating Nigeria's Rich Textile Traditions Since 2020
                    """)

                # Send the verification email with the token
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                )

                return Response({"message": "Account created. A verification email has been sent.",
                                "email":user.email}, status=status.HTTP_201_CREATED)

        if not user.is_active:
            return Response({"error": "Account inactive"}, status=400)
        
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        token = generate_magic_token(email)

        verification_link = request.build_absolute_uri(
            reverse('verify-magic-login', kwargs={'uidb64': uidb64, 'token': token, 'url_email': email})
        )
        
        send_mail(
            subject="Your Magic Login Link",
            message=textwrap.dedent(f"""
                Dear {user.first_name or 'Valued Customer'},

                Welcome back to Aso Oke & Aso Ofi Marketplace!

                Please verify your email address by clicking the link below:

                {verification_link}

                This link will expire in 10 minutes. If you didn't request this email, you can safely ignore it.

                Thanks,
                The Aso Oke & Aso Ofi Marketplace Team
                """),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False
        )

        return Response({"message": "Magic login link sent to email"}, status=200)
    
    
class MagicLoginView(APIView):
    swagger_schema = TaggedAutoSchema
    def get(self, request, uidb64, token, url_email):
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, id=uid)
        email = validate_magic_token(token)

        if not email:
            return redirect(f"{settings.BASE_URL}/verified-email-failed.html?email={url_email}&is_login=true")

        try:
            user = User.objects.get(id = user.id, email=email)
        except User.DoesNotExist:
            return redirect(f"{settings.BASE_URL}/verified-email-failed.html?email={url_email}&is_login=true")

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        group_names = ", ".join(user.groups.values_list('name', flat=True))

        # Build redirect with query params
        params = urlencode({
            "access": access_token,
            "refresh": str(refresh),
            "email": user.email,
            "name": user.first_name,
            "group": group_names
        })

        return redirect(f"{settings.BASE_URL}/index.html?{params}")
    
    

class UserProfileSummaryView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserOrderSummarySerializer
    swagger_schema = TaggedAutoSchema
    def get(self, request):
        user = request.user
        orders = Order.objects.filter(user=user).order_by('-created_at')
        data = {
            'first_name': user.first_name or "Not set",
            'last_name': user.last_name or "Not set",
            'email': user.email,
            'phone':user.phone or "Not set",
            'total_orders': orders.count(),
            'recent_orders': orders[:5]
        }
        serializer = UserOrderSummarySerializer(data)
        return Response(serializer.data)


class UpdateUserView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserUpdateSerializer
    swagger_schema = TaggedAutoSchema

    def put(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "User updated successfully",
            }, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    


# ADMIN VIEWS

from django.utils import timezone
from django.db.models import Count
from datetime import timedelta
from calendar import monthrange
from django.db.models import Sum
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

class DashboardAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DashboardSerializer
    swagger_schema = TaggedAutoSchema
    def get(self, request):
        admin = request.user

        # Only allow if user is a rider
        if not admin.groups.filter(name__iexact='admin').exists():
            return Response({"error": "Not authorized"}, status=401)
        
        
        now = timezone.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_end = current_month_start - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        
        # --- Current Month Counts ---
        products_current = Product.objects.filter(created_at__gte=current_month_start).count()
        orders_current = Order.objects.filter(created_at__gte=current_month_start).count()
        customers_current = Order.objects.filter(created_at__gte=current_month_start).values('user').distinct().count()

        # --- Last Month Counts ---
        products_last = Product.objects.filter(created_at__gte=last_month_start, created_at__lte=last_month_end).count()
        orders_last = Order.objects.filter(created_at__gte=last_month_start, created_at__lte=last_month_end).count()
        customers_last = Order.objects.filter(created_at__gte=last_month_start, created_at__lte=last_month_end).values('user').distinct().count()

        def calculate_change(current, last):
            if last == 0 and current == 0:
                return {"change": "0%", "direction": "no change"}
            if last == 0:
                return {"change": "+100%", "direction": "up"}
            percent_change = ((current - last) / last) * 100
            direction = "up" if percent_change >= 0 else "down"
            return {"change": f"{abs(percent_change):.2f}%", "direction": direction}
        
        order_stats = {
            "total_products": {
                "value": Product.objects.count(),
                **calculate_change(products_current, products_last),
            },
            "total_orders": {
                "value": Order.objects.count(),
                **calculate_change(orders_current, orders_last),
            },
            "total_customers": {
                "value": Order.objects.values('user').distinct().count(),
                **calculate_change(customers_current, customers_last),
            },
        }
        
        # --- Top Products ---
        top_products_qs = (
            OrderItem.objects
            .select_related('product')
            .values('product', 'product__title')
            .annotate(sold_count=Sum('quantity'))
            .order_by('-sold_count')[:10]
        )

        top_products_data = [
            {"product": OrderItem.objects.filter(product_id=item['product']).first().product, "sold_count": item['sold_count']}
            for item in top_products_qs
        ]

        top_products_serialized = DashboardTopProductSerializer(top_products_data, many=True).data

        # Stats
        stats = (
            OrderTracking.objects
            .values('status')
            .annotate(count=Count('id'))
            .order_by('status')
        )

        # Convert to desired format (name and value)
        status_data = [
            {
                "name": dict(OrderTracking.STATUS_CHOICES).get(stat['status'], stat['status']),
                "value": stat['count']
            }
            for stat in stats
        ]
        
        # Recent orders
        recent_orders = Order.objects.all()[:10]
        recent_orders_serialized = DashboardOrderSerializer(recent_orders, many=True).data
                
        
        # --- Response ---
        return Response({
            "stats": status_data,
            "order_status": order_stats,
            "top_products": top_products_serialized,
            "recent_orders": recent_orders_serialized,
        })
        
        
        
class ProductAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    swagger_schema = TaggedAutoSchema

    queryset = Product.objects.filter(display_product=True)
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['badge']
    ordering_fields = ['current_price', 'rating', 'created_at']

    def get_queryset(self):
        admin = self.request.user

        # Only allow if user is a rider
        if not admin.groups.filter(name__iexact='admin').exists():
            return Response({"error": "Not authorized"}, status=401)
        
        queryset = super().get_queryset()

        # Extract query parameters
        max_price = self.request.query_params.get('max_price')
        min_price = self.request.query_params.get('min_price')
        rating = self.request.query_params.get('rating')
        search = self.request.query_params.get('search')
        category = self.request.query_params.get('category')

        # Apply filters dynamically
        if min_price:
            queryset = queryset.filter(current_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(current_price__lte=max_price)
        if rating:
            queryset = queryset.filter(rating__gte=rating)
        if category:
            queryset = queryset.filter(category__name__icontains=category)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(product_number__icontains=search) |
                Q(category__name__icontains=search)
            )

        return queryset

    def get_serializer_context(self):
        return {"request": self.request}
    
    
    

class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = AdminOrderDetailSerializer
    filter_backends = [DjangoFilterBackend]
    
    def get_queryset(self):
        admin = self.request.user

        # Only allow if user is a rider
        if not admin.groups.filter(name__iexact='admin').exists():
            return Response({"error": "Not authorized"}, status=401)
        
        queryset = super().get_queryset()

        # Extract query parameters

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(order_number__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)
            )

        if queryset is None:
            queryset = queryset.filter(id=search)
        return queryset

    def get_serializer_context(self):
        return {"request": self.request}
    
    

class UpdateOrderTrackingAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderTrackingUpdateSerializer

    def post(self, request, *args, **kwargs):
        admin = self.request.user

        # Only allow if user is a rider
        if not admin.groups.filter(name__iexact='admin').exists():
            return Response({"error": "Not authorized"}, status=401)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tracking = serializer.update_status()
        return Response({
            "message": f"Order {tracking.order.order_number} updated to {tracking.status} successfully.",
        }, status=status.HTTP_200_OK)
        
        
        
class UserOrderListView(generics.ListAPIView):
    queryset = User.objects.prefetch_related('orders', 'groups').all()
    serializer_class = UserOrderListSerializer
    
    def get_queryset(self):
        admin = self.request.user

        # Only allow if user is a rider
        if not admin.groups.filter(name__iexact='admin').exists():
            return Response({"error": "Not authorized"}, status=401)
        
        queryset = super().get_queryset()

        # Extract query parameters

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(phone__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(groups__name__icontains=search)
            )

        if queryset is None:
            queryset = queryset.filter(id=search)
        return queryset.distinct()
