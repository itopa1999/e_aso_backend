from django.urls import path, include
from .views import *

urlpatterns = [
    path(
        "user/",
        include(
            [
                path("create/", RegisterUser.as_view()),
                path("login/", LoginView.as_view()),
                path('verify/email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify-email')
            ]
        )
    ),
]