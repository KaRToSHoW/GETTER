from django.contrib import admin
from django.db.models import Sum, Avg
from .models import Category, Product, Order, OrderItem, Review, Wishlist

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_product_count')
    search_fields = ('name',)
    list_filter = ('name',)
    inlines = []

    @admin.display(description='Количество продуктов')
    def get_product_count(self, obj):
        return obj.products.count()

class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = ('name', 'price', 'stock', 'is_available')

CategoryAdmin.inlines.append(ProductInline)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'category', 'price', 'stock', 'get_average_rating')
    search_fields = ('name', 'category__name', 'sku') 
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
    list_display = ('order_number', 'user', 'status', 'get_total_price', 'get_total_quantity', 'get_order_items_count', 'created_at')  # Заменили 'id' на 'order_number'
    list_filter = ('status',)
    date_hierarchy = 'created_at'
    search_fields = ('user__username', 'order_number')  # Ищем по 'order_number', а не по 'id'
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
        for order in queryset:
            self.message_user(request, f"Счет для заказа {order.order_number} отправлен.")
    send_invoice.short_description = "Отправить счет для выбранных заказов"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'get_price', 'get_total_price')
    list_filter = ('order', 'product', 'order__status') 
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
    ordering = ['user']

    @admin.display(description='Отрывок комментария')
    def get_comment_excerpt(self, obj):
        return obj.comment[:50] + '...' if obj.comment else 'Без комментария'

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')  # Добавьте 'added_at' в list_display
    list_filter = ('user', 'product')
    search_fields = ('user__username', 'product__name', 'product__sku')  # Добавьте поиск по 'product__sku'
    ordering = ['-added_at']  # Сортировка по времени (по убыванию)

