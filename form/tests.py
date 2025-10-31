from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Category, Form, Process

class APITest(TestCase):
    def setUp(self):
        # ایجاد کاربر و لاگین (SessionAuth برای IsAuthenticated)
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client = APIClient()
        self.client.login(username='testuser', password='password123')

        # ایجاد یک دسته‌بندی
        self.category = Category.objects.create(name='Category 1', description='Test category')

        # ایجاد فرم‌ها
        self.form1 = Form.objects.create(
            category=self.category,
            title='Form 1',
            question='What is your favorite color?',
            validation=True,
            min=1,
            max=50,
            force=True,              # فرم اجباری
            type='text'
        )
        # ✅ فیکس: افزودن options برای rating تا مقدار 4 معتبر باشد
        self.form2 = Form.objects.create(
            category=self.category,
            title='Form 2',
            question='Rate our service',
            validation=True,
            min=1,
            max=1,
            type='rating',
            options=['1', '2', '3', '4', '5']   # ← مهم
        )
        self.form3 = Form.objects.create(
            category=self.category,
            title='Form 3',
            question='Select your hobbies',
            validation=True,
            min=1,
            max=5,
            type='checkbox',
            options=['Reading', 'Sports', 'Gaming']
        )

        # ایجاد یک پروسس با فرم‌ها
        self.process = Process.objects.create(name='Process 1')
        self.process.forms.set([self.form1, self.form2, self.form3])

    def test_get_forms(self):
        response = self.client.get('/forms/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_create_category(self):
        data = {'name': 'Category 2', 'description': 'Another category'}
        response = self.client.post('/categories/', data, format='json')  # format برای JSON
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Category 2')

    def test_update_form(self):
        data = {'title': 'Updated Form 1'}
        response = self.client.patch(f'/forms/{self.form1.id}/update/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Form 1')

    def test_submit_answers(self):
        data = {
            'process_id': self.process.id,
            'answers': [
                {'form_id': self.form1.id, 'type': 'text', 'answer': 'Blue'},
                {'form_id': self.form2.id, 'type': 'rating', 'answer': 4},              # ← مجاز چون '4' در options هست
                {'form_id': self.form3.id, 'type': 'checkbox', 'answer': ['Reading', 'Gaming']}
            ]
        }
        response = self.client.post('/forms/answers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['answers']), 3)
        self.assertEqual(response.data['answers'][0]['answer'], 'Blue')
        # در مدل/سریالایزر پاسخ‌ها به رشته ذخیره می‌شوند
        self.assertEqual(response.data['answers'][1]['answer'], '4')

    def test_process_detail(self):
        response = self.client.get(f'/processes/{self.process.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['forms']), 3)
