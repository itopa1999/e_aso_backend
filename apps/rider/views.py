from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated

from apps.rider.BLL.Queries.RiderDashboard import RiderDashboardQuery
from apps.rider.BLL.Commands.SendOtp import SendOtpCommand
from apps.rider.BLL.Commands.VerifyOtp import VerifyOtpCommand
from apps.rider.BLL.Queries.RiderOrderDetails import RiderOrderDetailsQuery
from apps.rider.BLL.Commands.MarkOrderAsDelivered import MarkOrderAsDeliveredCommand
from apps.rider.serailizers import MarkOrderAsDeliveredSerializer, RiderDashboardSerializer, RiderOderDetailsSerializer, SendOtpSerializer, VerifyOtpSerializer
from utils.permissions import IsRiderPermission

# Create your views here.


class RiderDashboardView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsRiderPermission]
    serializer_class = RiderDashboardSerializer

    def get(self, request, *args, **kwargs):
        search = request.query_params.get("search")
        result = RiderDashboardQuery.query(request.user, search)

        profile_data = result.data["profile"]
        recent_orders = result.data["recent_deliveries"]
        
        page = self.paginate_queryset(recent_orders)
        if page is not None:
            paginated_serializer = self.get_serializer({
                "profile": profile_data,
                "recent_deliveries": page
            })
            return self.get_paginated_response(paginated_serializer.data)

        serializer = self.get_serializer({
            "profile": profile_data,
            "recent_deliveries": recent_orders
        })
        return Response(serializer.data, status=status.HTTP_200_OK)


class SendOtpView(generics.GenericAPIView):
    serializer_class = SendOtpSerializer
    permission_classes = [IsAuthenticated, IsRiderPermission]

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order_number = serializer.validated_data["order_number"]

        result = SendOtpCommand.execute(order_number)
        return Response(result.to_dict(), status=result.status_code)

class VerifyOtpView(generics.GenericAPIView):
    serializer_class = VerifyOtpSerializer
    permission_classes = [IsAuthenticated, IsRiderPermission]
    
    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_number = serializer.validated_data["order_number"]
        otp = serializer.validated_data["otp"]

        result = VerifyOtpCommand.execute(
            request, order_number, otp
        )
        
        print(result.to_dict())
        return Response(result.to_dict(), status=result.status_code)


class RiderOderDetailsView(generics.GenericAPIView):
    serializer_class = RiderOderDetailsSerializer
    permission_classes = [IsAuthenticated, IsRiderPermission]
    
    def post(self, request, *args, **kwargs):        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_number = serializer.validated_data["order_number"]

        result = RiderOrderDetailsQuery.execute(order_number, request)
        return Response(result.to_dict(), status=result.status_code)

    
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
        
        result = MarkOrderAsDeliveredCommand.execute(
            order_number,
            rider,
            delivery_notes,
            stars
        )
        return Response(result.to_dict(), status=result.status_code)