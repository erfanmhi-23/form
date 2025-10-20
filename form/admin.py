from django.contrib import admin
from .models import Category, Form, Process, Answer

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'create', 'update')
    search_fields = ('name',)
    list_filter = ('create','update')

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'force', 'question_num', 'view_count', 'create', 'update', 'answer_num', 'type', 'options')
    search_fields = ('title', 'question', 'description')
    list_filter = ('category', 'force', 'question_num', 'create', 'answer_num', 'type')

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('id', 'form', 'liner', 'view_count')
    search_fields = ('form__title',)
    list_filter = ('liner', 'form')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display  = ('id', 'form', 'process', 'type', 'answer')
    search_fields = ('answer', 'type', 'form__title')
    list_filter   = ('type', 'form')
