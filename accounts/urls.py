from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from accounts.views import *

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/email/', SendEmailOTPAPIView.as_view(), name='send_email_otp'),
    path('login/email/verify/', VerifyEmailOTPAPIView.as_view(), name='verify_email_otp'),
    path('google/callback/', ProfileAPIView.as_view() , name='google_callback'),
    path("signup/", SignupAPIView.as_view(), name="signup"),
    path("profile/delete/", DeleteAccountAPIView.as_view(), name="delete_account"),
    path("password/change/", ChangePasswordAPIView.as_view(), name="change_password"),
    ]
