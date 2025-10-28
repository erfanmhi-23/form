from rest_framework import serializers
from .models import FormReport,ReportSubscription

class FormReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormReport
        fields = ['form', 'view_count', 'answer_count', 'summary', 'updated_at']

class ReportSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSubscription
        fields = ['form', 'email', 'interval', 'last_sent', 'created_at']