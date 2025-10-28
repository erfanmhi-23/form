from django.db import models
from django.utils import timezone
from form.models import Form

class ReportSubscription(models.Model):
    REPORT_INTERVAL_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='subscriptions')
    email = models.EmailField()
    interval = models.CharField(max_length=10, choices=REPORT_INTERVAL_CHOICES, default='weekly')
    last_sent = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} - {self.form.title} ({self.interval})"

class FormReport(models.Model):
    form = models.OneToOneField(Form, on_delete=models.CASCADE, related_name='report')
    view_count = models.IntegerField(default=0)
    answer_count = models.IntegerField(default=0)
    summary = models.JSONField(default=dict)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Report for {self.form.title}"

