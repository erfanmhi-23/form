from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model, login, logout ,update_session_auth_hash 
from accounts.models import EmailOTP
from accounts.serializers import EmailSerializer, OTPWithPasswordSerializer,SignupSerializer, UserSerializer,DeleteAccountSerializer, ChangePasswordSerializer
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()

class SendEmailOTPAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = EmailOTP.generate_otp()
            EmailOTP.objects.create(email=email, code=otp_code)
    
            from django.core.mail import send_mail
            send_mail(
                "کد ورود شما",
                f"کد ورود شما: {otp_code}",
                "noreply@example.com",
                [email],
                fail_silently=False,
            )
            
            request.session['email'] = email
            return Response({"detail": "کد OTP به ایمیل شما ارسال شد."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailOTPAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPWithPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        code = serializer.validated_data['code']
        password = serializer.validated_data['password']

        email = request.session.get('email')
        if not email:
            return Response({"detail": "ایمیل در session وجود ندارد."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            otp = EmailOTP.objects.filter(email=email, code=code, is_used=False).latest('created_at')
        except EmailOTP.DoesNotExist:
            return Response({"detail": "کد اشتباه است یا پیدا نشد."}, status=status.HTTP_400_BAD_REQUEST)

        if otp.is_expired():
            return Response({"detail": "کد منقضی شده است."}, status=status.HTTP_400_BAD_REQUEST)

        # استفاده شده علامت زده شود
        otp.is_used = True
        otp.save()

        # اگر کاربر وجود ندارد، بسازیم
        user, created = User.objects.get_or_create(username=email, defaults={'email': email})

        # پسورد کاربر را تنظیم کنیم
        user.set_password(password)
        user.save()

        # ورود کاربر
        login(request, user)

        # تولید JWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        serializer_user = UserSerializer(user)
        return Response({
            "detail": "ورود موفقیت‌آمیز بود.",
            "user": serializer_user.data,
            "access": access_token,
            "refresh": str(refresh)
        }, status=status.HTTP_200_OK)


class SignupAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            serializer_user = UserSerializer(user)
            return Response({
                "detail": "ثبت‌نام موفق بود.",
                "user": serializer_user.data,
                "refresh": str(refresh),
                "access": access_token
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail":"پروفایل ذخیره شد.", "user": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteAccountAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = DeleteAccountSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        password = serializer.validated_data['password']
        if not request.user.check_password(password):
            return Response({"password": ["رمز عبور اشتباه است."]}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        logout(request)
        user.delete()
        return Response({"detail":"حساب شما حذف شد."}, status=status.HTTP_200_OK)


class ChangePasswordAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        user = request.user
        if not user.check_password(old_password):
            return Response({"old_password": ["رمز عبور فعلی اشتباه است."]}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        
        update_session_auth_hash(request, user)
        return Response({"detail":"رمز عبور با موفقیت تغییر کرد."}, status=status.HTTP_200_OK)
