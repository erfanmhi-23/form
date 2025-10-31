from rest_framework import serializers
from .models import Category, Form, Process, Answer

class CategorySerializer(serializers.ModelSerializer):
    class Meta :
        model = Category
        fields = ['id', 'name', 'description', 'create', 'update' ]

class FormSerializer(serializers.ModelSerializer):
    class Meta :
        model = Form
        fields = [
            'id', 'category', 'title', 'question', 'description',
            'validation', 'max', 'force', 'create', 'update',
            'password', 'view_count', 'question_num', 'type', 'options'
        ]
    def validate(self, data):
        instance = Form(**data)
        instance.clean()
        return data

class ProcessSerializer(serializers.ModelSerializer):
    forms = FormSerializer(many=True, read_only=True)  
    form_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Form.objects.all(), write_only=True, source='forms'
    ) 

    class Meta:
        model = Process
        fields = ['id', 'name', 'liner', 'password', 'view_count', 'forms', 'form_ids']

class AnswerSerializer(serializers.ModelSerializer):
    answer = serializers.JSONField()
    
    class Meta:
        model = Answer
        fields = ['id', 'process', 'form', 'type', 'answer']