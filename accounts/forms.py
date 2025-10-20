from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

class EmailForm(forms.Form):
    email = forms.EmailField(label="ایمیل", max_length=255)

class SignupForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ["username", "first_name", "last_name", "email"]

class UserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "email", "phone_number", "sex"]

class DeleteAccountForm(forms.Form):
    password = forms.CharField(label="رمز عبور", widget=forms.PasswordInput)

