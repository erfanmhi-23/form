from rest_framework import serializers
from .models import Category, Form, Process, Answer

class CategorySerializer(serializers.ModelSerializer):
    class Meta :
        model = Category
        fields = ['id', 'name', 'description', 'create', 'update' ]

class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = [
            'id', 'category', 'title', 'question', 'description',
            'validation', 'max', 'force', 'create', 'update',
            'password', 'view_count', 'question_num', 'type', 'options'
        ]

class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = ['id', 'form', 'liner', 'password', 'view_count']

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'process', 'form', 'type', 'answer']