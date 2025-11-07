from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import User, EmailOTP
from rest_framework_simplejwt.tokens import RefreshToken

class TestAccountsViews(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123", email="test@example.com")
        self.refresh = RefreshToken.for_user(self.user)
        self.auth_header = f'Bearer {self.refresh.access_token}'

    def test_signup(self):
        url = reverse("signup")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123"
        }
        res = self.client.post(url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_send_email_otp(self):
        url = reverse("send_email_otp")
        data = {"email": "otpuser@example.com"}
        res = self.client.post(url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(EmailOTP.objects.filter(email="otpuser@example.com").exists())

    def test_verify_email_otp(self):
        otp_code = "123456"
        EmailOTP.objects.create(email="otpuser2@example.com", code=otp_code)
        session = self.client.session
        session['email'] = "otpuser2@example.com"
        session.save()

        url = reverse("verify_email_otp")
        data = {"code": otp_code, "password": "newpass123"}
        res = self.client.post(url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_profile_retrieve(self):
        url = reverse("profileview")
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['username'], self.user.username)

    def test_change_password(self):
        url = reverse("change_password")
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        data = {"old_password": "password123", "new_password": "newpass123"}
        res = self.client.post(url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpass123"))

    def test_delete_account(self):
        url = reverse("delete_account")
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        data = {"password": "password123"}
        res = self.client.post(url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(User.objects.filter(username=self.user.username).exists())
