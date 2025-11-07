from django.db import models
from django.utils import timezone
from form.models import Form , Process
from accounts.models import User

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

class Conclusion(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="user")
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name='report')
    view_count = models.IntegerField(default=0)
    answer_count = models.IntegerField(default=0)
    answer_list = models.JSONField(default=dict)
    mean_rating = models.FloatField(blank=True,null=True)
    usable_category = models.CharField(max_length=255, blank=True, null=True) #here <------------------------

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Report for {self.process}"

