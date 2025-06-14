from django.contrib import admin
from django.db.models import Sum, Avg
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
import os
from typing import Any, List, Optional, Tuple, Union, Dict, Set
from django.http.request import HttpRequest
from django.db.models.query import QuerySet
from .models import Category, Product, Order, OrderItem, Review, Wishlist

# Регистрируем шрифт DejaVuSerif
FONT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'fonts', 'DejaVuSerif.ttf')
pdfmetrics.registerFont(TTFont('DejaVuSerif', FONT_PATH))

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели Category.
    
    Attributes:
        list_display: Поля, отображаемые в списке категорий
        search_fields: Поля, по которым осуществляется поиск
        list_filter: Поля, по которым осуществляется фильтрация
        inlines: Встроенные формы для связанных моделей
    """
    list_display = ('name', 'get_product_count')
    search_fields = ('name',)
    list_filter = ('name',)
    inlines = []

    @admin.display(description='Количество продуктов')
    def get_product_count(self, obj: Category) -> int:
        """
        Возвращает количество продуктов в категории.
        
        Args:
            obj: Объект категории
            
        Returns:
            Количество продуктов в категории
        """
        return obj.products.count()

class ProductInline(admin.TabularInline):
    """
    Встроенная форма для отображения продуктов внутри категории.
    
    Attributes:
        model: Модель, для которой создается встроенная форма
        extra: Количество дополнительных пустых форм
        fields: Поля, отображаемые в форме
    """
    model = Product
    extra = 0
    fields = ('name', 'price', 'stock', 'is_available')

CategoryAdmin.inlines.append(ProductInline)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели Product.
    
    Attributes:
        list_display: Поля, отображаемые в списке продуктов
        search_fields: Поля, по которым осуществляется поиск
        list_filter: Поля, по которым осуществляется фильтрация
        autocomplete_fields: Поля с автозаполнением
        ordering: Порядок сортировки по умолчанию
    """
    list_display = ('sku', 'name', 'category', 'price', 'discount', 'stock', 'get_average_rating')
    search_fields = ('name', 'category__name', 'sku') 
    list_filter = ('category', 'price', 'discount', 'is_available')
    autocomplete_fields = ['category']
    ordering = ['name']

    @admin.display(description='Средний рейтинг')
    def get_average_rating(self, obj: Product) -> Union[float, str]:
        """
        Возвращает средний рейтинг продукта.
        
        Args:
            obj: Объект продукта
            
        Returns:
            Средний рейтинг продукта или строку "Нет отзывов"
        """
        average_rating = obj.reviews.aggregate(average=Avg('rating'))['average']
        return round(average_rating, 2) if average_rating else 'Нет отзывов'


class OrderItemInline(admin.TabularInline):
    """
    Встроенная форма для отображения позиций заказа внутри заказа.
    
    Attributes:
        model: Модель, для которой создается встроенная форма
        extra: Количество дополнительных пустых форм
        readonly_fields: Поля, доступные только для чтения
    """
    model = OrderItem
    extra = 0
    readonly_fields = ('get_price', 'get_total_price')

    @admin.display(description='Цена за позицию')
    def get_price(self, obj: OrderItem) -> float:
        """
        Возвращает цену за единицу товара с учетом скидки.
        
        Args:
            obj: Объект позиции заказа
            
        Returns:
            Цена за единицу товара с учетом скидки
        """
        return obj.product.get_discounted_price()

    @admin.display(description='Итоговая цена')
    def get_total_price(self, obj: OrderItem) -> float:
        """
        Возвращает итоговую цену за позицию заказа.
        
        Args:
            obj: Объект позиции заказа
            
        Returns:
            Итоговая цена за позицию заказа
        """
        return obj.product.get_discounted_price() * obj.quantity

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели Order.
    
    Attributes:
        list_display: Поля, отображаемые в списке заказов
        list_filter: Поля, по которым осуществляется фильтрация
        date_hierarchy: Поле для иерархической навигации по датам
        search_fields: Поля, по которым осуществляется поиск
        readonly_fields: Поля, доступные только для чтения
        inlines: Встроенные формы для связанных моделей
        autocomplete_fields: Поля с автозаполнением
        ordering: Порядок сортировки по умолчанию
        actions: Действия для выбранных заказов
        fieldsets: Группировка полей в форме редактирования
    """
    list_display = ('order_number', 'user', 'status', 'get_total_price', 'get_total_quantity', 'get_order_items_count', 'created_at')  # Заменили 'id' на 'order_number'
    list_filter = ('status',)
    date_hierarchy = 'created_at'
    search_fields = ('user__username', 'order_number')  # Ищем по 'order_number', а не по 'id'
    readonly_fields = ('get_total_price', 'get_shipping_address')
    inlines = [OrderItemInline]
    autocomplete_fields = ['user']
    ordering = ['-created_at']
    actions = ['mark_as_shipped', 'mark_as_delivered', 'mark_as_canceled', 'send_invoice', 'generate_pdf']
    fieldsets = (
        ('Основная информация', {
            'fields': ('order_number', 'user', 'status', 'get_total_price', 'created_at', 'updated_at')
        }),
        ('Информация о доставке', {
            'fields': ('shipping_city', 'shipping_street', 'shipping_house', 'shipping_apartment', 
                      'shipping_postal_code', 'shipping_comment', 'get_shipping_address')
        }),
    )

    @admin.display(description='Общая цена')
    def get_total_price(self, obj: Order) -> float:
        """
        Возвращает общую цену заказа.
        
        Args:
            obj: Объект заказа
            
        Returns:
            Общая цена заказа
        """
        return obj.calculate_total_price()

    @admin.display(description='Количество товаров')
    def get_total_quantity(self, obj: Order) -> int:
        """
        Возвращает общее количество товаров в заказе.
        
        Args:
            obj: Объект заказа
            
        Returns:
            Общее количество товаров в заказе
        """
        return sum(item.quantity for item in obj.items.all())

    @admin.display(description='Количество позиций')
    def get_order_items_count(self, obj: Order) -> int:
        """
        Возвращает количество позиций в заказе.
        
        Args:
            obj: Объект заказа
            
        Returns:
            Количество позиций в заказе
        """
        return obj.items.count()
        
    @admin.display(description='Полный адрес доставки')
    def get_shipping_address(self, obj: Order) -> str:
        """
        Возвращает полный адрес доставки.
        
        Args:
            obj: Объект заказа
            
        Returns:
            Строка с полным адресом доставки
        """
        return obj.get_shipping_address()

    def mark_as_shipped(self, request: HttpRequest, queryset: QuerySet) -> None:
        """
        Отмечает выбранные заказы как отправленные.
        
        Args:
            request: Объект запроса
            queryset: QuerySet с выбранными заказами
        """
        queryset.update(status='shipped')
    mark_as_shipped.short_description = "Отметить как отправленные"

    def mark_as_delivered(self, request: HttpRequest, queryset: QuerySet) -> None:
        """
        Отмечает выбранные заказы как доставленные.
        
        Args:
            request: Объект запроса
            queryset: QuerySet с выбранными заказами
        """
        queryset.update(status='delivered')
    mark_as_delivered.short_description = "Отметить как доставленные"

    def mark_as_canceled(self, request: HttpRequest, queryset: QuerySet) -> None:
        """
        Отмечает выбранные заказы как отмененные.
        
        Args:
            request: Объект запроса
            queryset: QuerySet с выбранными заказами
        """
        queryset.update(status='canceled')
    mark_as_canceled.short_description = "Отметить как отмененные"

    def send_invoice(self, request: HttpRequest, queryset: QuerySet) -> None:
        """
        Отправляет счет для выбранных заказов.
        
        Args:
            request: Объект запроса
            queryset: QuerySet с выбранными заказами
        """
        for order in queryset:
            self.message_user(request, f"Счет для заказа {order.order_number} отправлен.")
    send_invoice.short_description = "Отправить счет для выбранных заказов"

    def generate_pdf(self, request: HttpRequest, queryset: QuerySet) -> HttpResponse:
        """
        Генерирует PDF-файл с информацией о выбранных заказах.
        
        Args:
            request: Объект запроса
            queryset: QuerySet с выбранными заказами
            
        Returns:
            HttpResponse с PDF-файлом
        """
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="orders.pdf"'
        
        p = canvas.Canvas(response, pagesize=A4)
        y = 800  # Starting y position
        
        for order in queryset:
            # Order header
            p.setFont("DejaVuSerif", 16)
            p.drawString(50, y, f"Заказ №{order.order_number}")
            y -= 30
            
            p.setFont("DejaVuSerif", 12)
            p.drawString(50, y, f"Клиент: {order.user.username}")
            y -= 20
            p.drawString(50, y, f"Статус: {order.get_status_display()}")
            y -= 20
            p.drawString(50, y, f"Дата создания: {order.created_at.strftime('%d.%m.%Y %H:%M')}")
            y -= 20
            
            # Shipping address
            if order.shipping_city or order.shipping_street:
                p.drawString(50, y, f"Адрес доставки: {order.get_shipping_address()}")
                y -= 40
            else:
                y -= 20
            
            # Items header
            p.setFont("DejaVuSerif", 12)
            p.drawString(50, y, "Товар")
            p.drawString(300, y, "Кол-во")
            p.drawString(400, y, "Цена")
            y -= 20
            
            # Items
            p.setFont("DejaVuSerif", 12)
            for item in order.items.all():
                if y < 50:  # Check if we need a new page
                    p.showPage()
                    y = 800
                    p.setFont("DejaVuSerif", 12)
                
                p.drawString(50, y, str(item.product.name)[:35])
                p.drawString(300, y, str(item.quantity))
                p.drawString(400, y, f"{item.price} ₽")
                y -= 20
            
            # Total
            y -= 20
            p.setFont("DejaVuSerif", 12)
            p.drawString(300, y, f"Итого: {order.calculate_total_price()} ₽")
            
            # Add some space before next order
            y -= 60
            
            if y < 100:  # Start new page if not enough space
                p.showPage()
                y = 800
        
        p.showPage()
        p.save()
        return response
    
    generate_pdf.short_description = "Сгенерировать PDF"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели OrderItem.
    
    Attributes:
        list_display: Поля, отображаемые в списке позиций заказа
        list_filter: Поля, по которым осуществляется фильтрация
        search_fields: Поля, по которым осуществляется поиск
    """
    list_display = ('order', 'product', 'quantity', 'get_price', 'get_total_price')
    list_filter = ('order', 'product', 'order__status') 
    search_fields = ('order__id', 'product__name')

    @admin.display(description='Цена за единицу')
    def get_price(self, obj: OrderItem) -> float:
        """
        Возвращает цену за единицу товара с учетом скидки.
        
        Args:
            obj: Объект позиции заказа
            
        Returns:
            Цена за единицу товара с учетом скидки
        """
        return obj.product.get_discounted_price()

    @admin.display(description='Итоговая цена')
    def get_total_price(self, obj: OrderItem) -> float:
        """
        Возвращает итоговую цену за позицию заказа.
        
        Args:
            obj: Объект позиции заказа
            
        Returns:
            Итоговая цена за позицию заказа
        """
        return obj.product.get_discounted_price() * obj.quantity


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели Review.
    
    Attributes:
        list_display: Поля, отображаемые в списке отзывов
        list_filter: Поля, по которым осуществляется фильтрация
        date_hierarchy: Поле для иерархической навигации по датам
        search_fields: Поля, по которым осуществляется поиск
        ordering: Порядок сортировки по умолчанию
    """
    list_display = ('user', 'product', 'rating', 'created_at', 'get_comment_excerpt')
    list_filter = ('rating',)
    date_hierarchy = 'created_at'
    search_fields = ('user__username', 'product__name')
    ordering = ['user']

    @admin.display(description='Отрывок комментария')
    def get_comment_excerpt(self, obj: Review) -> str:
        """
        Возвращает отрывок комментария отзыва.
        
        Args:
            obj: Объект отзыва
            
        Returns:
            Отрывок комментария или строка "Без комментария"
        """
        return obj.comment[:50] + '...' if obj.comment else 'Без комментария'

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели Wishlist.
    
    Attributes:
        list_display: Поля, отображаемые в списке желаемого
        list_filter: Поля, по которым осуществляется фильтрация
        search_fields: Поля, по которым осуществляется поиск
        ordering: Порядок сортировки по умолчанию
    """
    list_display = ('user', 'product', 'added_at')  # Добавьте 'added_at' в list_display
    list_filter = ('user', 'product')
    search_fields = ('user__username', 'product__name', 'product__sku')  # Добавьте поиск по 'product__sku'
    ordering = ['-added_at']  # Сортировка по времени (по убыванию)

