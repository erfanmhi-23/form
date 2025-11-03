from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from accounts.models import User


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Form(models.Model):
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,blank=True,related_name='forms')
    title = models.CharField(max_length=255)
    question = models.CharField(max_length=255)
    description = models.CharField(max_length=255,blank=True)
    validation = models.BooleanField()
    min = models.IntegerField(default=1)
    max = models.IntegerField(null=True, blank=True)
    force = models.BooleanField(default=False)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    password = models.CharField(max_length=255, blank=True, null=True)
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

    
    def clean(self):
        super().clean()

 
        if self.type in ['checkbox', 'select']:
            if not self.options or len(self.options) == 0:
                raise ValidationError("برای نوع checkbox یا select باید گزینه‌ها (options) پر شود.")
            for opt in self.options:
                if not isinstance(opt, str):
                    raise ValidationError("تمام گزینه‌ها باید رشته (string) باشند.")

   
        elif self.type == 'rating':
            if not self.options or len(self.options) == 0:
                self.options = ['1', '2', '3', '4', '5']  
            else:

                for opt in self.options:
                    try:
                        int(opt)
                    except ValueError:
                        raise ValidationError("تمام گزینه‌ها برای نوع rating باید عددی باشند.")

  
        elif self.type == 'text':
            if self.options and len(self.options) > 0:
                raise ValidationError("برای نوع text نیازی به options نیست.")
            
    def save(self, *args, **kwargs):
        if self.type == 'rating' and (not self.options or len(self.options) == 0):
            self.options = ['1', '2', '3', '4', '5']
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Process(models.Model):
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,blank=True,related_name='process_category')
    name = models.CharField(max_length=255)
    forms = models.ManyToManyField('Form',through='ProcessForm',related_name='processes')
    liner = models.BooleanField(default=False)
    password = models.CharField(max_length=255, blank=True, null=True)
    view_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'process'

    def __str__(self):
        return f"Process for {self.name}"
    
class Answer(models.Model):
    process = models.ForeignKey(Process, on_delete=models.CASCADE,related_name='answers')
    form = models.ForeignKey(Form, on_delete=models.CASCADE,related_name='answers')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='answers')
    type = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)

    class Meta:
        db_table = 'answer'

    def __str__(self):
        return self.answer
  

class ProcessForm(models.Model):
    process = models.ForeignKey(Process, on_delete=models.CASCADE)
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ('process', 'form')
