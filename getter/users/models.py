from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Почта")
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True, verbose_name="Картинка профиля")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username

    def get_profile_image_url(self):
            """ Возвращает корректный URL к изображению профиля """
            if self.profile_image:
                return f"{settings.MEDIA_URL}{self.profile_image}"
            return f"{settings.MEDIA_URL}profile_images/default_profile_image.png"