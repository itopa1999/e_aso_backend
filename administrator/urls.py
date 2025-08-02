from django.urls import path, include
from .views import *

urlpatterns = [
    path(
        "user/",
        include(
            [
                path("magic-login/", SendMagicLinkView.as_view()),
                path("verify/magic/login/<uidb64>/<token>/<url_email>/", MagicLoginView.as_view(), name="verify-magic-login"),
                path("resend-link/", ResendVerificationEmailView.as_view()),
                path("profile/", UserProfileSummaryView.as_view()),
                path("update/profile/", UpdateUserView.as_view()),
                path('verify/email/<uidb64>/<token>/<url_email>/', VerifyEmailView.as_view(), name='verify-email')
            ]
        )
    ),
]