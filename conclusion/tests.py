from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from unittest.mock import patch
from form.models import Form, Category, Process, Answer
from .models import FormReport, ReportSubscription

class FormReportViewsTestCase(APITestCase):
    def setUp(self):
        # ایجاد کاربران
        self.admin_user = User.objects.create_user(username="admin", password="admin123", is_staff=True)
        self.normal_user = User.objects.create_user(username="user", password="user123")
        
        # ایجاد فرم و گزارش
        self.form = Form.objects.create(title="Test Form")
        self.report = FormReport.objects.create(
            form=self.form,
            summary={
                1: {"type": "rating", "count": 5, "average": 3.4},
                2: {"type": "select", "count": 3, "options": {"A": 2, "B": 1}}
            }
        )

        # ایجاد دسته‌بندی، فرآیند و پاسخ
        self.category = Category.objects.create(name="Test Category")
        self.category.forms.add(self.form)
        self.process = Process.objects.create(form=self.form)
        self.answer = Answer.objects.create(process=self.process, type="text", answer="Sample answer")

        self.client = APIClient()

    def test_get_form_report_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f"/report/form/{self.form.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summary", response.data)

    def test_get_form_report_as_non_admin(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(f"/report/form/{self.form.id}/")
        self.assertEqual(response.status_code, 403)

    def test_subscribe_report(self):
        self.client.force_authenticate(user=self.normal_user)
        data = {"email": "test@example.com", "interval": "weekly"}
        response = self.client.post(f"/report/subscribe/{self.form.id}/", data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["interval"], "weekly")
        self.assertTrue(ReportSubscription.objects.filter(email="test@example.com").exists())

    @patch("django.core.mail.send_mail")
    def test_send_form_report_email(self, mock_send_mail):
        self.client.force_authenticate(user=self.normal_user)
        # شبیه‌سازی ایمیل در session
        session = self.client.session
        session['email'] = 'test@example.com'
        session.save()

        mock_send_mail.return_value = 1  # شبیه‌سازی موفقیت‌آمیز ارسال ایمیل

        response = self.client.post(f"/report/send-email/{self.form.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Report sent to", response.data["detail"])
        mock_send_mail.assert_called_once()

    def test_all_answers_report(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get("/report/all-answers/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("categories", response.data)
        self.assertEqual(response.data["categories"][0]["name"], "Test Category")
        self.assertEqual(len(response.data["categories"][0]["forms"]), 1)
        self.assertEqual(len(response.data["categories"][0]["forms"][0]["processes"]), 1)
        self.assertEqual(len(response.data["categories"][0]["forms"][0]["processes"][0]["answers"]), 1)
