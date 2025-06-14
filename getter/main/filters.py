import django_filters
from django.db.models import Avg, QuerySet
from typing import Any, Dict, List, Optional, Union
from .models import Product, Category

class ProductFilter(django_filters.FilterSet):
    """
    Фильтр для модели Product с расширенным функционалом фильтрации.
    
    Attributes:
        name: Фильтр по названию товара (частичное совпадение)
        description: Фильтр по описанию товара (частичное совпадение)
        sku: Фильтр по артикулу товара (частичное совпадение)
        min_price: Фильтр по минимальной цене товара
        max_price: Фильтр по максимальной цене товара
        category: Фильтр по категории товара
        category_name: Фильтр по названию категории (частичное совпадение)
        is_available: Фильтр по наличию товара
        min_discount: Фильтр по минимальному проценту скидки
        has_discount: Фильтр по наличию скидки
        min_rating: Фильтр по минимальному рейтингу товара
        ordering: Сортировка результатов
    """
    name = django_filters.CharFilter(lookup_expr='icontains', help_text="Поиск по названию товара")
    description = django_filters.CharFilter(lookup_expr='icontains', help_text="Поиск по описанию товара")
    sku = django_filters.CharFilter(lookup_expr='icontains', help_text="Поиск по артикулу")
    
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte', help_text="Минимальная цена")
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte', help_text="Максимальная цена")
    
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        help_text="Фильтр по категории товара (ID категории)"
    )
    
    category_name = django_filters.CharFilter(
        field_name='category__name',
        lookup_expr='icontains',
        help_text="Поиск по названию категории"
    )
    
    is_available = django_filters.BooleanFilter(help_text="Фильтр по наличию товара")
    
    min_discount = django_filters.NumberFilter(
        field_name='discount', 
        lookup_expr='gte', 
        help_text="Минимальный процент скидки"
    )
    
    has_discount = django_filters.BooleanFilter(
        field_name='discount',
        method='filter_has_discount',
        help_text="Наличие скидки (true/false)"
    )
    
    min_rating = django_filters.NumberFilter(
        method='filter_by_rating',
        help_text="Минимальный рейтинг товара"
    )
    
    ordering = django_filters.OrderingFilter(
        fields=(
            ('price', 'price'),
            ('name', 'name'),
            ('creation_date', 'creation_date'),
            ('discount', 'discount'),
        ),
        help_text="Сортировка результатов. Используйте '-' для обратного порядка (например: -price)"
    )
    
    def filter_has_discount(self, queryset: QuerySet, name: str, value: bool) -> QuerySet:
        """
        Фильтр по наличию скидки.
        
        Args:
            queryset: Исходный QuerySet продуктов
            name: Название поля для фильтрации
            value: Значение фильтра (True/False)
            
        Returns:
            Отфильтрованный QuerySet с товарами, имеющими или не имеющими скидку
        """
        if value:  # Если True, возвращаем товары со скидкой > 0
            return queryset.filter(discount__gt=0)
        # Если False, возвращаем товары без скидки
        return queryset.filter(discount=0)
    
    def filter_by_rating(self, queryset: QuerySet, name: str, value: float) -> QuerySet:
        """
        Фильтр по минимальному рейтингу.
        
        Args:
            queryset: Исходный QuerySet продуктов
            name: Название поля для фильтрации
            value: Минимальное значение рейтинга
            
        Returns:
            Отфильтрованный QuerySet с товарами, имеющими средний рейтинг не ниже указанного
        """
        # Аннотируем queryset средним рейтингом и фильтруем
        return queryset.annotate(average_rating=Avg('reviews__rating')).filter(average_rating__gte=value)
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'sku', 'min_price', 'max_price', 
            'category', 'category_name', 'is_available', 'min_discount', 
            'has_discount', 'min_rating'
        ] 