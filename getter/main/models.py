from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Категория")
    image = models.ImageField(upload_to='category_images/', blank=True, null=True, verbose_name="Изображение")  # Новое поле

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category-list')

class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True, verbose_name="Артикул")
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    stock = models.PositiveIntegerField(verbose_name="Количество")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products", verbose_name="Категория")
    image = models.ImageField(upload_to='product_images/', blank=True, null=True, verbose_name="Картинка товара")
    is_available = models.BooleanField(default=True, verbose_name="В наличии")
    specifications = models.JSONField(blank=True, null=True, verbose_name="Характеристики")

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'pk': self.pk})
    
class OrderManager(models.Manager):
    def pending(self):
        return self.filter(status='pending')

    def completed(self):
        return self.filter(status__in=['shipped', 'delivered'])


class Order(models.Model):
    objects = OrderManager()
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('assembling', 'В сборке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('canceled', 'Отменен')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders", verbose_name="Пользователь")
    products = models.ManyToManyField(Product, through='OrderItem', related_name="orders")  # ManyToMany с through
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True)
    order_number = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="Номер заказа")  # Новое поле для номера заказа

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def calculate_total_price(self):
        return sum(item.price for item in self.order_items.all())

    def save(self, *args, **kwargs):
        # Генерация номера заказа, если его нет
        if not self.order_number:
            self.order_number = f"ORDER{self.id:05d}" 
        if self.pk:
            self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Заказ №{self.order_number}" 
    
    def get_absolute_url(self):
        return reverse('order_detail', kwargs={'pk': self.pk})

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items", verbose_name="Товар")
    quantity = models.PositiveIntegerField( verbose_name="Количество")

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказов"

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def price(self):
        return self.product.price * self.quantity  # Цена = количество * цена товара


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)] 

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews", verbose_name="Пользоваетль")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews", verbose_name="Товар")
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, default=5, verbose_name="Рейтинг")
    comment = models.TextField(blank=True, null=True, verbose_name="Отзыв")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"Отзыв от {self.user.username} - {self.rating}"

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist", verbose_name="Пользователь")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlisted_by", verbose_name="Продукт")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлен")

    class Meta:
        unique_together = ('user', 'product')
        verbose_name = "Список желаемого"
        verbose_name_plural = "Списки желаемого"

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"