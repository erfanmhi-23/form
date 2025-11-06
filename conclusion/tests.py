from unittest import expectedFailure
from unittest.mock import patch
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import ReportSubscription, Conclusion
from .serializers import FormReportSerializer, ReportSubscriptionSerializer
# ⚠️ Form و بقیه مدل‌ها از اپِ جداگانه 'form' می‌آیند
from form.models import Category, Form, Process, Answer

User = get_user_model()

def make_user(email="staff@example.com", password="pass12345", is_staff=False, is_superuser=False):
    # اگر create_user پروژه‌ات username می‌خواهد، اینجا را مطابقش تغییر بده
    user = User.objects.create_user(email=email, password=password)
    user.is_staff = is_staff
    user.is_superuser = is_superuser
    user.save()
    return user

class SubscribeReportViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = make_user(is_staff=True)
        self.user = make_user(email="u@example.com")
        self.cat = Category.objects.create(name="Cat A")
        self.form = Form.objects.create(title="Form A", category=self.cat)

    def test_requires_auth(self):
        url = reverse("subscribe-report", kwargs={"form_id": self.form.id})
        res = self.client.post(url, {"email": "a@b.com", "interval": "weekly"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_email(self):
        self.client.force_authenticate(self.user)
        url = reverse("subscribe-report", kwargs={"form_id": self.form.id})
        res = self.client.post(url, {"interval": "weekly"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_interval(self):
        self.client.force_authenticate(self.user)
        url = reverse("subscribe-report", kwargs={"form_id": self.form.id})
        res = self.client.post(url, {"email": "a@b.com", "interval": "daily"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_then_update(self):
        self.client.force_authenticate(self.user)
        url = reverse("subscribe-report", kwargs={"form_id": self.form.id})

        res = self.client.post(url, {"email": "a@b.com", "interval": "weekly"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(
            ReportSubscription.objects.filter(form=self.form, email="a@b.com", interval="weekly").exists()
        )

        res = self.client.post(url, {"email": "a@b.com", "interval": "monthly"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(
            ReportSubscription.objects.filter(form=self.form, email="a@b.com", interval="monthly").exists()
        )


class FormReportViewTests(TestCase):
    """
    ویوی فعلی Conclusion.objects.get(form_id=form_id) می‌زند
    ولی Conclusion فیلد form ندارد ⇒ انتظار 500 (FieldError).
    وقتی ویو را به process__form_id اصلاح کنی، تست را تغییر بده.
    """
    def setUp(self):
        self.client = APIClient()
        self.staff = make_user(is_staff=True)
        self.user = make_user(email="u@example.com")
        self.cat = Category.objects.create(name="Cat A")
        self.form = Form.objects.create(title="Form A", category=self.cat)
        self.process = Process.objects.create(form=self.form, view_count=1)

        self.conclusion = Conclusion.objects.create(
            user=self.staff,
            process=self.process,
            view_count=3,
            answer_count=1,
            answer_list={"q1": "a"},
            mean_rating=4.0,
        )

    def test_requires_staff(self):
        self.client.force_authenticate(self.user)
        url = reverse("form-report", kwargs={"form_id": self.form.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_currently_fielderror_500(self):
        self.client.force_authenticate(self.staff)
        url = reverse("form-report", kwargs={"form_id": self.form.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class SendFormReportEmailAPIViewTests(TestCase):
    """
    ویو دنبال Conclusion با form می‌گردد (وجود ندارد) و سپس report.summary را می‌خواند (وجود ندارد) ⇒ 500.
    مسیر خوشحال را expectedFailure می‌گذاریم تا بعد از اصلاح، پاسش کنی.
    """
    def setUp(self):
        self.client = APIClient()
        self.staff = make_user(is_staff=True)
        self.cat = Category.objects.create(name="Cat A")
        self.form = Form.objects.create(title="Form A", category=self.cat)
        self.process = Process.objects.create(form=self.form, view_count=1)

        self.conclusion = Conclusion.objects.create(
            user=self.staff,
            process=self.process,
            view_count=3,
            answer_count=1,
            answer_list={"q1": "a"},
        )
        self.url = reverse("send-report-email", kwargs={"form_id": self.form.id})

    def test_missing_email_in_session(self):
        self.client.force_authenticate(self.staff)
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Email not found in session", str(res.data))

    @expectedFailure
    def test_happy_path_expected_failure_until_you_fix_model_or_view(self):
        """
        بعد از اعمال یکی از این‌ها، این تست را از expectedFailure خارج کن:
          - اضافه کردن summary = JSONField(default=dict, blank=True) به Conclusion
          - تغییر ویو به Conclusion.objects.get(process__form=form)
        """
        from django.core import mail

        self.client.force_authenticate(self.staff)
        session = self.client.session
        session["email"] = "dest@example.com"
        session.save()

        res = self.client.post(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Form Report:", mail.outbox[0].subject)


class AllAnswersReportViewTests(TestCase):
    """
    این ویو با روابط Category→Form→Process→Answer کار می‌کند (همه در اپ 'form').
    """
    def setUp(self):
        self.client = APIClient()
        self.staff = make_user(is_staff=True)

        self.cat1 = Category.objects.create(name="Cat 1")
        self.cat2 = Category.objects.create(name="Cat 2")

        self.form1 = Form.objects.create(title="Form 1", category=self.cat1)
        self.form2 = Form.objects.create(title="Form 2", category=self.cat1)
        self.form3 = Form.objects.create(title="Form 3", category=self.cat2)

        self.p11 = Process.objects.create(form=self.form1, view_count=3)
        self.p12 = Process.objects.create(form=self.form1, view_count=0)
        self.p21 = Process.objects.create(form=self.form2, view_count=2)
        self.p31 = Process.objects.create(form=self.form3, view_count=1)

        Answer.objects.create(process=self.p11, type="text", answer="hello")
        Answer.objects.create(process=self.p11, type="select", answer="opt1")
        Answer.objects.create(process=self.p12, type="checkbox", answer=["a", "b"])
        Answer.objects.create(process=self.p31, type="rating", answer="5")

    def test_structure_ok(self):
        self.client.force_authenticate(self.staff)
        url = reverse("all-answers-report")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        cats = res.data.get("categories", [])
        self.assertEqual(len(cats), 2)

        cat1 = next(c for c in cats if c["name"] == "Cat 1")
        self.assertEqual(len(cat1["forms"]), 2)

        f1 = next(f for f in cat1["forms"] if f["title"] == "Form 1")
        self.assertEqual(len(f1["processes"]), 2)

        p11 = next(p for p in f1["processes"] if p["id"] == self.p11.id)
        self.assertGreaterEqual(len(p11["answers"]), 2)
        sample = p11["answers"][0]
        self.assertIn("type", sample)
        self.assertIn("answer", sample)


class SerializerSmokeTests(TestCase):
    """
    تست سبک برای Serializerها روی مدل فعلی.
    """
    def setUp(self):
        self.user = make_user()
        self.cat = Category.objects.create(name="Cat A")
        self.form = Form.objects.create(title="Form A", category=self.cat)
        self.process = Process.objects.create(form=self.form, view_count=1)
        self.conclusion = Conclusion.objects.create(
            user=self.user,
            process=self.process,
            view_count=5,
            answer_count=2,
            answer_list={"q1": "a"},
            mean_rating=4.5,
        )

    def test_form_report_serializer(self):
        data = FormReportSerializer(self.conclusion).data
        self.assertIn("process", data)
        self.assertIn("view_count", data)
        self.assertIn("answer_count", data)
        self.assertIn("answer_list", data)
        self.assertIn("updated_at", data)

    def test_report_subscription_serializer(self):
        sub = ReportSubscription.objects.create(form=self.form, email="a@b.com", interval="weekly")
        data = ReportSubscriptionSerializer(sub).data
        self.assertIn("email", data)
        self.assertIn("interval", data)
        self.assertIn("created_at", data)
