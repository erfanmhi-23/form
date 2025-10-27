from django.db import models
from django.contrib.postgres.fields import ArrayField

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Form(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='forms'
    )
    title = models.CharField(max_length=255)
    question = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    validation = models.CharField(max_length=255)
    max = models.IntegerField()
    force = models.BooleanField(default=False)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    password = models.CharField(max_length=255)#blank True
    view_count = models.IntegerField(default=0)
    question_num = models.BooleanField(default=False)
    type = models.CharField(
        max_length=255,
        choices=[
            ('select', 'Select'),
            ('checkbox', 'Checkbox'),
            ('text', 'Text'),
            ('rating', 'Rating')
        ] 
    )
    options = ArrayField(                     
        base_field=models.CharField(max_length=255),
        blank=True,
        null=True,
        default=list
    )
    def __str__(self):
        return self.title


class Process(models.Model):
    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        related_name='processes'
    )
    liner = models.BooleanField(default=False)
    password = models.CharField(max_length=255, blank=True, null=True)
    view_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'process'

    def __str__(self):
        return f"Process for {self.form}"
    
class Answer(models.Model):
    process = models.ForeignKey(Process, on_delete=models.CASCADE,related_name='answers')
    form = models.ForeignKey(Form, on_delete=models.CASCADE,related_name='answers')
    type = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)

    class Meta:
        db_table = 'answer'

    def __str__(self):
        return self.answer