from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import User
from form.models import Form, Category
from rest_framework_simplejwt.tokens import RefreshToken

class TestFormViews(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.category = Category.objects.create(name="Test Category")

        self.form = Form.objects.create(
            category=self.category,
            title="Initial Title",
            question="Initial Question",
            description="Initial Description",
            validation=True,
            max=10,
            force=False,
            password=None,
            type="text",
            options=[]
        )

    def test_form_list(self):
        url = reverse("form-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res.data) >= 1)

    def test_form_create(self):
        url = reverse("form-list")
        data = {
            "category": self.category.id,
            "title": "New Form",
            "question": "This is a new question",
            "description": "Some description",
            "validation": True,
            "max": 20,
            "force": True,
            "password": None,
            "type": "text",
            "options": []
        }
        res = self.client.post(url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['title'], "New Form")

    def test_form_detail(self):
        url = reverse("form-detail", args=[self.form.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], self.form.title)

    def test_form_update_put(self):
        url = reverse("form-update", args=[self.form.id])
        data = {
            "category": self.category.id,
            "title": "Updated Title",
            "question": "Updated Question",
            "description": "Updated Description",
            "validation": True,
            "max": 15,
            "force": False,
            "password": None,
            "type": "select",
            "options": ["opt1", "opt2"]
        }
        res = self.client.put(url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.form.refresh_from_db()
        self.assertEqual(self.form.title, "Updated Title")
        self.assertEqual(self.form.options, ["opt1", "opt2"])

    def test_form_update_patch(self):
        url = reverse("form-update", args=[self.form.id])
        data = {
            "title": "Patched Title"
        }
        res = self.client.patch(url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.form.refresh_from_db()
        self.assertEqual(self.form.title, "Patched Title")

    def test_form_delete(self):
        url = reverse("form-delete", args=[self.form.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Form.objects.filter(id=self.form.id).exists())
