from django.apps import AppConfig


class MainConfig(AppConfig):
    """
    Конфигурация приложения main.
    
    Attributes:
        default_auto_field: Тип поля для автоматически создаваемых первичных ключей
        name: Имя приложения
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
