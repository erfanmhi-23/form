from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import EmailOTP

class EmailOTPTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.email = "test@example.com"
    
    def test_send_email_otp_creates_record(self):
        response = self.client.post(reverse("send_email_otp"), {"email": self.email})
        self.assertEqual(response.status_code, 302)
        otp = EmailOTP.objects.filter(email=self.email).first()
        self.assertIsNotNone(otp)
        self.assertFalse(otp.is_used)
    
    def test_verify_email_otp_success(self):
        otp_code = EmailOTP.generate_otp()
        otp = EmailOTP.objects.create(email=self.email, code=otp_code)
        session = self.client.session
        session['email'] = self.email
        session.save()
        response = self.client.post(reverse("verify_email_otp"), {"code": otp_code})
        self.assertRedirects(response, reverse("home"))
        otp.refresh_from_db()
        self.assertTrue(otp.is_used)
    
    def test_verify_email_otp_wrong_code(self):
        EmailOTP.objects.create(email=self.email, code="123456")
        session = self.client.session
        session['email'] = self.email
        session.save()
        response = self.client.post(reverse("verify_email_otp"), {"code": "000000"})
        self.assertRedirects(response, reverse("verify_email_otp"))