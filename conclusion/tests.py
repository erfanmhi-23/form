from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from form.models import Category, Form, Process, Answer
from conclusion.models import Conclusion, ReportSubscription  # ← اینجا اصلاح شد

class BaseAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Users
        self.user = User.objects.create_user(
            username="u1", email="u1@example.com", password="pass12345"
        )
        self.staff = User.objects.create_user(
            username="admin", email="admin@example.com", password="pass12345", is_staff=True
        )

        # Domain objects (Category -> Form -> Process -> Answer)
        self.category = Category.objects.create(name="Cat A")
        # اگر مدل Form فیلد category ندارد، این خط را با مدل واقعی خودت هماهنگ کن
        self.form = Form.objects.create(title="Form A", category=self.category)
        # اگر Process فیلد دیگری برای اتصال به فرم دارد، جایگزین کن
        self.process = Process.objects.create(form=self.form)

        # یک Answer نمونه (type/answer را با فیلدهای واقعی مدل خودت هماهنگ کن)
        self.answer_text = Answer.objects.create(
            process=self.process,
            type="text",
            answer="hello world"
        )

        # یک Conclusion برای گزارش‌ها
        self.conclusion = Conclusion.objects.create(
            user=self.user,
            process=self.process,
            view_count=3,
            answer_count=1,
            answer_list={"q1": "a1"},
            mean_rating=4.5,
            usable_category="ok"
        )

        # لاگین پیش‌فرض کاربر معمولی
        self.client.login(username="u1", password="pass12345")


class TestAllReportView(BaseAPITest):
    def test_get_all_report_requires_auth(self):
        self.client.logout()
        url = reverse("all_report")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_all_report_ok(self):
        url = reverse("all_report")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("summary", res.data)
        self.assertIn("data", res.data)
        self.assertIsInstance(res.data["data"], list)
        self.assertGreaterEqual(res.data["summary"].get("total_reports", 0), 1)


class TestFormReportView(BaseAPITest):
    def test_form_report_requires_staff(self):
        url = reverse("form-report", args=[self.process.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_form_report_staff_sees_data(self):
        self.client.logout()
        self.client.login(username="admin", password="pass12345")

        url = reverse("form-report", args=[self.process.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.data, list)
        self.assertGreaterEqual(len(res.data), 1)
        keys = {"process", "view_count", "answer_count", "answer_list", "updated_at"}
        self.assertTrue(keys.issubset(set(res.data[0].keys())))

    def test_form_report_not_found(self):
        self.client.logout()
        self.client.login(username="admin", password="pass12345")
        url = reverse("form-report", args=[999999])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class TestSubscribeReportView(BaseAPITest):
    def test_subscribe_missing_email(self):
        url = reverse("subscribe-report", args=[self.form.id])
        res = self.client.post(url, data={"interval": "weekly"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscribe_invalid_interval(self):
        url = reverse("subscribe-report", args=[self.form.id])
        res = self.client.post(url, data={"email": "x@y.com", "interval": "yearly"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscribe_ok_and_update_interval(self):
        url = reverse("subscribe-report", args=[self.form.id])
        # create
        res = self.client.post(url, data={"email": "x@y.com", "interval": "weekly"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ReportSubscription.objects.count(), 1)
        sub = ReportSubscription.objects.first()
        self.assertEqual(sub.interval, "weekly")
        # update
        res = self.client.post(url, data={"email": "x@y.com", "interval": "monthly"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        sub.refresh_from_db()
        self.assertEqual(sub.interval, "monthly")


class TestSendFormReportEmailAPIView(BaseAPITest):
    def test_send_email_requires_session_email_returns_400(self):
        """
        این تست عمداً ایمیل سشن را ست نمی‌کند تا قبل از رسیدن به خط
        Conclusion.objects.get(form=form) با 400 برگردد (چون مدل Conclusion فیلد form ندارد).
        """
        url = reverse("send-report-email", args=[self.form.id])
        res = self.client.post(url, data={}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data.get("detail"), "Email not found in session")


class TestAllAnswersReportView(BaseAPITest):
    def test_all_answers_structure(self):
        url = reverse("all-answers-report")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("categories", res.data)
        cats = res.data["categories"]
        self.assertIsInstance(cats, list)
        self.assertGreaterEqual(len(cats), 1)

        cat0 = cats[0]
        self.assertIn("forms", cat0)
        self.assertIsInstance(cat0["forms"], list)
        self.assertGreaterEqual(len(cat0["forms"]), 1)

        form0 = cat0["forms"][0]
        self.assertIn("processes", form0)
        self.assertIsInstance(form0["processes"], list)
        self.assertGreaterEqual(len(form0["processes"]), 1)

        proc0 = form0["processes"][0]
        self.assertIn("answers", proc0)
        self.assertIsInstance(proc0["answers"], list)
        self.assertGreaterEqual(len(proc0["answers"]), 1)
        self.assertEqual(proc0["answers"][0]["answer"], "hello world")


class TestModels(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="u2", email="u2@example.com", password="pass12345"
        )
        self.category = Category.objects.create(name="Cat B")
        self.form = Form.objects.create(title="Form B", category=self.category)
        self.process = Process.objects.create(form=self.form)

    def test_report_subscription_str_and_defaults(self):
        sub = ReportSubscription.objects.create(
            form=self.form, email="sub@example.com", interval="weekly", last_sent=None
        )
        self.assertIn("sub@example.com", str(sub))
        self.assertIn("Form B", str(sub))
        self.assertEqual(sub.interval, "weekly")
        self.assertIsNone(sub.last_sent)
        self.assertIsNotNone(sub.created_at)

    def test_conclusion_str_and_fields(self):
        c = Conclusion.objects.create(
            user=self.user,
            process=self.process,
            view_count=0,
            answer_count=2,
            answer_list={"q1": "a1", "q2": "a2"},
            mean_rating=3.0,
            usable_category="ok",
        )
        self.assertIn("Report for", str(c))
        self.assertEqual(c.answer_count, 2)
        self.assertEqual(c.answer_list["q1"], "a1")
        self.assertIsNotNone(c.updated_at)

    def test_conclusion_ordering_desc_by_updated_at(self):
        c1 = Conclusion.objects.create(user=self.user, process=self.process)
        c2 = Conclusion.objects.create(user=self.user, process=self.process)
        latest = list(Conclusion.objects.all())[0]
        self.assertEqual(latest.id, c2.id)
