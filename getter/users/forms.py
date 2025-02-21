from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import User

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import User

class RegistrationForm(UserCreationForm):
    """ Форма регистрации с аватаром, именем и фамилией """
    first_name = forms.CharField(required=True, label="Имя")
    last_name = forms.CharField(required=True, label="Фамилия")
    email = forms.EmailField(required=True, label="Email")
    profile_image = forms.ImageField(required=False, label="Аватар")

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "profile_image", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if self.cleaned_data["profile_image"]:
            user.profile_image = self.cleaned_data["profile_image"]
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    """ Форма входа """
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Неверный логин или пароль")
        return self.cleaned_data

