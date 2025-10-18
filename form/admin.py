from django.contrib import admin
from .models import Category, Form, Text, SelectCheckbox, Rating, Process

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'create', 'update')
    search_fields = ('name',)
    list_filter = ('create',)

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'force', 'question_num', 'view_count', 'create', 'update')
    search_fields = ('title', 'question', 'description')
    list_filter = ('category', 'force', 'question_num', 'create')

@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ('id', 'form', 'text')
    search_fields = ('text', 'form__title')
    list_filter = ('form',)

@admin.register(SelectCheckbox)
class SelectCheckboxAdmin(admin.ModelAdmin):
    list_display = ('id', 'form', 'multiple_choices', 'choices')
    search_fields = ('choices', 'form__title')
    list_filter = ('multiple_choices', 'form')

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display  = ('id', 'form', 'rating', 'emoji')
    search_fields = ('emoji', 'form__title')
    list_filter   = ('rating', 'form')

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('id', 'form', 'liner', 'view_count')
    search_fields = ('form__title',)
    list_filter = ('liner', 'form')
