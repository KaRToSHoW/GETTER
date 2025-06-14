from django.contrib.auth import get_user_model
from rest_framework import serializers
from typing import Dict, Any

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.
    
    Attributes:
        profile_image_url: Вычисляемое поле для URL изображения профиля
    """
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_superuser', 'profile_image', 'profile_image_url']

    def get_profile_image_url(self, obj: User) -> str:
        """
        Получает URL изображения профиля пользователя.
        
        Args:
            obj: Объект пользователя
            
        Returns:
            URL изображения профиля
        """
        return obj.get_profile_image_url()
