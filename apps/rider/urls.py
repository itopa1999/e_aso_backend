from django.urls import path, include
from .views import *

urlpatterns = [
    path('rider/', RiderDashboardView.as_view()),
    path('orders/send-otp/', SendOtpView.as_view(), name='send-otp'),
    path('orders/verify-otp/', VerifyOtpView.as_view(), name='verify-otp'),
    path('orders/confirm/', MarkOrderAsDeliveredView.as_view()),
    path('orders/rider-details/', RiderOderDetailsView.as_view()),

]