from django.contrib import admin
from .models import ReportSubscription,FormReport

@admin.register(ReportSubscription) 
class ReportSubscriptionAdmin(admin.ModelAdmin) :
    list_display = ("form", "email", "interval", "last_sent")

@admin.register(FormReport)
class FormReportAdmin(admin.ModelAdmin):
    list_display = ("form", "view_count", "answer_count")