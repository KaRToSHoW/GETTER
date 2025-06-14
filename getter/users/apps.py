from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Конфигурация приложения users.
    
    Attributes:
        default_auto_field: Тип поля для автоматически создаваемых первичных ключей
        name: Имя приложения
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
