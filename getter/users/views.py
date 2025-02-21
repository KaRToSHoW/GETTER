from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from .forms import RegistrationForm, LoginForm  # Создадим их ниже

def registration(request):
    """ Регистрация пользователя """
    if request.method == "POST":
        form = RegistrationForm(request.POST, request.FILES)  # Передаём request.FILES
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Вы успешно зарегистрировались!")
            return redirect("profile")
    else:
        form = RegistrationForm()

    return render(request, "users/registration.html", {"form": form})


def user_login(request):
    """ Вход в систему """
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, "Вы вошли в систему!")
                return redirect("profile")
            else:
                messages.error(request, "Неверные данные!")
    else:
        form = LoginForm()
    
    return render(request, "users/login.html", {"form": form})

@login_required
def profile(request):
    """ Профиль пользователя """
    return render(request, "users/profile.html", {"user": request.user})

def user_logout(request):
    """ Выход из системы """
    logout(request)
    messages.info(request, "Вы вышли из системы.")
    return redirect("login")
