from django.urls import path
from accounts.views import *

urlpatterns = [
    path('login/email/', send_email_otp, name='send_email_otp'),
    path('login/email/verify/', verify_email_otp, name='verify_email_otp'),
    path('google/callback/', google_callback , name='google_callback'),
    path("signup/", signup, name="signup"),
    path("profile/delete/", delete_account, name="delete_account"),
    path("password/change/", change_password, name="change_password"),
    ]
