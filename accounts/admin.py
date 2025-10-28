from django.contrib import admin
from accounts.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin) :
    list_display = ('username','first_name','is_superuser')
    search_fields = ('username',)
    list_filter = ('is_superuser',)
