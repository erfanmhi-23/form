from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'category'

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
    description = models.TextField(blank=True, null=True)
    validation = models.CharField(max_length=255, blank=True, null=True)  
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


class Rating(models.Model):
    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    rating = models.IntegerField()
    emoji = models.CharField(max_length=50) #what is type of emoji ???

    class Meta:
        db_table = 'rating'

    def __str__(self):
        return f"Rating {self.rating} for {self.form}"


class Text(models.Model):
    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        related_name='texts'
    )
    text = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'text'

    def __str__(self):
        return f"Text for {self.form}"


class SelectCheckbox(models.Model):
    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        related_name='select_checkboxes'
    )
    choices = models.CharField(max_length=255)
    multiple_choices = models.BooleanField(default=False)

    class Meta:
        db_table = 'select_checkbox'

    def __str__(self):
        return f"Choices for {self.form}"


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
