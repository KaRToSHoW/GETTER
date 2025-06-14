"""
URL конфигурация для приложения users.

Определяет маршруты для работы с пользователями, включая:
- API для управления пользователями
- Аутентификацию с использованием JWT токенов
- Регистрацию пользователей
- Управление профилем пользователя
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Создаем роутер для API
router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', views.register_api, name='register_api'),
    
    # Profile management
    path('profile/', views.profile, name='profile'),
    path('profile/image/', views.upload_profile_image, name='upload-profile-image'),
    path('profile/image/remove/', views.remove_profile_image, name='remove-profile-image'),
]



