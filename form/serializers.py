from rest_framework import serializers
from .models import Category, Form, Process, Answer , ProcessForm

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
        fields = ['id', 'process', 'form', 'type', 'answer','user']

class ProcessFormSerializer(serializers.ModelSerializer):
    form_title = serializers.CharField(source='form.title', read_only=True)
    form_type = serializers.CharField(source='form.type', read_only=True)
    form_options = serializers.ListField(source='form.options', read_only=True)

    class Meta:
        model = ProcessForm
        fields = ['id', 'process', 'form', 'order', 'form_title', 'form_type', 'form_options']

class ProcessSerializer(serializers.ModelSerializer):
    # فرم‌ها با اطلاعات کامل و order
    process_forms = serializers.SerializerMethodField()
    
    # فقط شناسه فرم‌ها برای ایجاد/ویرایش
    form_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Form.objects.all(), write_only=True
    )

    class Meta:
        model = Process
        fields = ['id', 'name', 'liner', 'password', 'view_count', 'form_ids']

    def get_process_forms(self, obj):
        process_forms_qs = obj.processform_set.select_related('form').order_by('order')
        return [
            {
                'form_id': pf.form.id,
                'title': pf.form.title,
                'type': pf.form.type,
                'options': pf.form.options,
                'order': pf.order,
            }
            for pf in process_forms_qs
        ]

    def update(self, instance, validated_data):
        form_ids = validated_data.pop('form_ids', [])
        instance = super().update(instance, validated_data)

        if form_ids:
            # پاک کردن فرم‌های قدیمی و اضافه کردن فرم‌های جدید
            instance.forms.set(form_ids)
            # اگر میخوای order را حفظ یا reset کنی، اینجا می‌توان مدیریت کرد
        return instance
