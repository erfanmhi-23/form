from django.contrib import admin
from .models import ReportSubscription, Conclusion

@admin.register(ReportSubscription) 
class ReportSubscriptionAdmin(admin.ModelAdmin) :
    list_display = ("form", "email", "interval", "last_sent")

@admin.register(Conclusion)
class ConclusionAdmin(admin.ModelAdmin):
    list_display = ("process", "view_count", "answer_count")