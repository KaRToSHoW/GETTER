from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from typing import Optional

class User(AbstractUser):
    """
    Расширенная модель пользователя.
    
    Attributes:
        email: Электронная почта пользователя (уникальная)
        profile_image: Изображение профиля пользователя
    """
    email = models.EmailField(unique=True, verbose_name="Почта")
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True, verbose_name="Картинка профиля")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        """
        Строковое представление пользователя.
        
        Returns:
            Имя пользователя
        """
        return self.username

    def get_profile_image_url(self) -> str:
        """
        Возвращает корректный URL к изображению профиля.
        Если изображение не установлено, возвращает URL к изображению по умолчанию.
        
        Returns:
            URL к изображению профиля
        """
        if self.profile_image:
            return f"{settings.MEDIA_URL}{self.profile_image}"
        return f"{settings.MEDIA_URL}profile_images/default_profile_image.png"