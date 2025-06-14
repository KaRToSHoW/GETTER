from django.contrib import admin
from main.models import Review
from .models import User
from typing import List, Tuple, Dict, Any

class ReviewInline(admin.TabularInline):
    """
    Встроенная форма для отображения отзывов пользователя.
    
    Attributes:
        model: Модель отзыва
        extra: Количество дополнительных пустых форм
        readonly_fields: Поля, доступные только для чтения
    """
    model = Review
    extra = 0
    readonly_fields = ('product', 'rating', 'comment', 'created_at')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели User.
    
    Attributes:
        list_display: Поля, отображаемые в списке пользователей
        list_filter: Поля, по которым осуществляется фильтрация
        search_fields: Поля, по которым осуществляется поиск
        readonly_fields: Поля, доступные только для чтения
        list_display_links: Поля, являющиеся ссылками на детальную информацию
        inlines: Встроенные формы для связанных моделей
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('last_login',)
    list_display_links = ('username',)
    inlines = [ReviewInline]