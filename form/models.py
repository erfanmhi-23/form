from django.db import models

class Form(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    question = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    validatioin = models.CharField(max_length=255, blank=True, null=True)  # assuming typo in 'validation'
    max = models.IntegerField(blank=True, null=True)
    min = models.IntegerField(blank=True, null=True)
    force = models.BooleanField(default=False)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    view_count = models.IntegerField(default=0)
    question_num = models.BooleanField(default=False)

    class Meta:
        db_table = 'form'

    def __str__(self):
        return self.title
