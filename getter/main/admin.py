from django.contrib import admin
from django.db.models import Sum
from .models import Category, Product, Order, OrderItem, Review, Wishlist

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_product_count')
    search_fields = ('name',)
    list_filter = ('name',)

    @admin.display(description='Количество продуктов')
    def get_product_count(self, obj):
        return obj.products.count()

from django.db.models import Avg

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'get_average_rating')
    search_fields = ('name', 'category__name')
    list_filter = ('category', 'price')
    autocomplete_fields = ['category']
    ordering = ['name']

    @admin.display(description='Средний рейтинг')
    def get_average_rating(self, obj):
        average_rating = obj.reviews.aggregate(average=Avg('rating'))['average']
        return round(average_rating, 2) if average_rating else 'Нет отзывов'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('get_price', 'get_total_price')

    @admin.display(description='Цена за позицию')
    def get_price(self, obj):
        return obj.product.price

    @admin.display(description='Итоговая цена')
    def get_total_price(self, obj):
        return obj.price

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'get_total_price', 'get_total_quantity', 'get_order_items_count', 'created_at')
    list_filter = ('status',)
    date_hierarchy = 'created_at'
    search_fields = ('user__username', 'id')
    readonly_fields = ('get_total_price',)
    inlines = [OrderItemInline]
    autocomplete_fields = ['user']
    ordering = ['-created_at']
    actions = ['mark_as_shipped', 'mark_as_delivered', 'mark_as_canceled', 'send_invoice']

    @admin.display(description='Общая цена')
    def get_total_price(self, obj):
        return obj.calculate_total_price()

    @admin.display(description='Количество товаров')
    def get_total_quantity(self, obj):
        return sum(item.quantity for item in obj.items.all())

    @admin.display(description='Количество позиций')
    def get_order_items_count(self, obj):
        return obj.items.count()

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
    mark_as_shipped.short_description = "Отметить как отправленные"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
    mark_as_delivered.short_description = "Отметить как доставленные"

    def mark_as_canceled(self, request, queryset):
        queryset.update(status='canceled')
    mark_as_canceled.short_description = "Отметить как отмененные"

    def send_invoice(self, request, queryset):
        # Пример отправки счета (реализовать логику)
        for order in queryset:
            # Пример вывода сообщения, а не реальной отправки
            self.message_user(request, f"Счет для заказа {order.id} отправлен.")
    send_invoice.short_description = "Отправить счет для выбранных заказов"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'get_price', 'get_total_price')
    list_filter = ('order', 'product')
    search_fields = ('order__id', 'product__name')

    @admin.display(description='Цена за единицу')
    def get_price(self, obj):
        return obj.product.price

    @admin.display(description='Итоговая цена')
    def get_total_price(self, obj):
        return obj.price

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at', 'get_comment_excerpt')
    list_filter = ('rating',)
    date_hierarchy = 'created_at'
    search_fields = ('user__username', 'product__name')

    @admin.display(description='Отрывок комментария')
    def get_comment_excerpt(self, obj):
        return obj.comment[:50] + '...' if obj.comment else 'Без комментария'

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')
    list_filter = ('user', 'product')
    search_fields = ('user__username', 'product__name')
