from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from decimal import Decimal
from typing import Optional, Union, List, Dict, Any

class Category(models.Model):
    """
    Модель категории товаров.
    
    Attributes:
        name: Название категории
        image: Изображение категории
    """
    name = models.CharField(max_length=255, unique=True, verbose_name="Категория")
    image = models.ImageField(upload_to='category_images/', blank=True, null=True, verbose_name="Изображение")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self) -> str:
        """
        Строковое представление категории.
        
        Returns:
            Название категории
        """
        return self.name
    
    def get_absolute_url(self) -> str:
        """
        Получение абсолютного URL для категории.
        
        Returns:
            URL страницы со списком категорий
        """
        return reverse('category-list')

class Product(models.Model):
    """
    Модель товара.
    
    Attributes:
        sku: Артикул товара
        name: Название товара
        description: Описание товара
        price: Цена товара
        discount: Скидка в процентах
        stock: Количество товара на складе
        category: Категория товара
        image: Изображение товара
        manufacturer_url: URL сайта производителя
        documentation: Документация к товару
        is_available: Доступность товара
        specifications: Характеристики товара в формате JSON
        creation_date: Дата поступления товара
        updated_at: Дата и время обновления товара
    """
    sku = models.CharField(max_length=50, unique=True, verbose_name="Артикул")
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    discount = models.PositiveSmallIntegerField(default=0, verbose_name="Скидка в %")
    stock = models.PositiveIntegerField(verbose_name="Количество")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products", verbose_name="Категория")
    image = models.ImageField(upload_to='product_images/', blank=True, null=True, verbose_name="Картинка товара")
    manufacturer_url = models.URLField(verbose_name="Сайт производителя", blank=True, null=True)
    documentation = models.FileField(upload_to='product_docs/', blank=True, null=True, verbose_name="Документация")
    is_available = models.BooleanField(default=True, verbose_name="В наличии")
    specifications = models.JSONField(blank=True, null=True, verbose_name="Характеристики")
    creation_date = models.DateTimeField(default=timezone.now, verbose_name="Дата поступления")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self) -> str:
        """
        Строковое представление товара.
        
        Returns:
            Название товара
        """
        return self.name

    def get_absolute_url(self) -> str:
        """
        Получение абсолютного URL для товара.
        
        Returns:
            URL страницы с детальной информацией о товаре
        """
        return reverse('product-detail', kwargs={'pk': self.pk})
        
    def get_discounted_price(self) -> Decimal:
        """
        Возвращает цену товара с учетом скидки.
        
        Returns:
            Цена товара со скидкой
        """
        if self.discount == 0:
            return self.price
        discount_amount = (self.price * self.discount) / 100
        return round(self.price - discount_amount, 2)

class OrderManager(models.Manager):
    """
    Менеджер для модели Order с дополнительными методами запросов.
    """
    
    def pending(self) -> models.QuerySet:
        """
        Получение всех заказов в статусе "ожидает".
        
        Returns:
            QuerySet с заказами в статусе "ожидает"
        """
        return self.filter(status='pending')

    def completed(self) -> models.QuerySet:
        """
        Получение всех выполненных заказов.
        
        Returns:
            QuerySet с заказами в статусе "отправлен" или "доставлен"
        """
        return self.filter(status__in=['shipped', 'delivered'])


class Order(models.Model):
    """
    Модель заказа.
    
    Attributes:
        user: Пользователь, создавший заказ
        products: Товары в заказе (через OrderItem)
        status: Статус заказа
        total_price: Общая стоимость заказа
        created_at: Дата создания заказа
        updated_at: Дата обновления заказа
        order_number: Уникальный номер заказа
        shipping_city: Город доставки
        shipping_street: Улица доставки
        shipping_house: Дом доставки
        shipping_apartment: Квартира доставки
        shipping_postal_code: Почтовый индекс доставки
        shipping_comment: Комментарий к доставке
    """
    objects = OrderManager()
    STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('assembling', 'В сборке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('canceled', 'Отменен'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders", verbose_name="Пользователь")
    products = models.ManyToManyField(Product, through='OrderItem', related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Общая стоимость")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")
    order_number = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="Номер заказа")  
    
    # Поля информации о доставке
    shipping_city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город")
    shipping_street = models.CharField(max_length=200, blank=True, null=True, verbose_name="Улица")
    shipping_house = models.CharField(max_length=50, blank=True, null=True, verbose_name="Дом")
    shipping_apartment = models.CharField(max_length=50, blank=True, null=True, verbose_name="Квартира")
    shipping_postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name="Почтовый индекс")
    shipping_comment = models.TextField(blank=True, null=True, verbose_name="Комментарий к доставке")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def calculate_total_price(self) -> Decimal:
        """
        Вычисляет общую стоимость заказа на основе товаров в корзине с учетом скидок.
        
        Returns:
            Общая стоимость заказа
        """
        total = Decimal('0.00')
        for item in self.items.all():
            if item.product:
                # Используем метод get_discounted_price для учета скидки
                total += item.product.get_discounted_price() * item.quantity
        return total

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Переопределенный метод сохранения для автоматической генерации номера заказа
        и обновления общей стоимости.
        
        Args:
            *args: Позиционные аргументы для метода save родительского класса
            **kwargs: Именованные аргументы для метода save родительского класса
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)  # Сначала сохраняем объект, чтобы получить ID
        
        # Генерация номера заказа только для новых объектов
        if is_new and not self.order_number:
            self.order_number = f"ORDER{self.id:05d}"
            super().save(update_fields=['order_number'])  # Сохраняем только поле order_number
            
        # Обновляем total_price только если объект уже существует и имеет товары
        if not is_new:
            new_total = self.calculate_total_price()
            if self.total_price != new_total:
                self.total_price = new_total
                super().save(update_fields=['total_price'])  # Сохраняем только поле total_price

    def __str__(self) -> str:
        """
        Строковое представление заказа.
        
        Returns:
            Строка с номером заказа
        """
        return f"Заказ №{self.order_number}" 
    
    def get_absolute_url(self) -> str:
        """
        Получение абсолютного URL для заказа.
        
        Returns:
            URL страницы с детальной информацией о заказе
        """
        return reverse('order_detail', kwargs={'pk': self.pk})

    def update_status_by_time(self) -> bool:
        """
        Обновляет статус заказа на основе времени.
        
        Правила:
        - Если заказ в статусе 'pending' более 7 дней, отменяем его
        - Если заказ в статусе 'shipped' более 3 дней, помечаем как доставленный
        
        Returns:
            bool: True, если статус был изменен, иначе False
        """
        import datetime
        from django.utils import timezone
        
        now = timezone.now()
        status_changed = False
        
        # Отменяем заказы, которые в обработке более 7 дней
        if self.status == 'pending':
            days_pending = (now - self.created_at).days
            if days_pending > 7:
                self.status = 'canceled'
                status_changed = True
        
        # Помечаем отправленные заказы как доставленные через 3 дня
        elif self.status == 'shipped':
            # Проверяем, когда заказ был отмечен как отправленный
            # Используем updated_at как приблизительное время отправки
            days_shipped = (now - self.updated_at).days
            if days_shipped > 3:
                self.status = 'delivered'
                status_changed = True
        
        if status_changed:
            self.save(update_fields=['status', 'updated_at'])
            
        return status_changed
        
    def get_shipping_address(self) -> str:
        """
        Возвращает полный адрес доставки в виде строки.
        
        Returns:
            Строка с полным адресом доставки или сообщение об отсутствии адреса
        """
        address_parts = []
        if self.shipping_city:
            address_parts.append(self.shipping_city)
        if self.shipping_street:
            address_parts.append(self.shipping_street)
        if self.shipping_house:
            address_parts.append(f"дом {self.shipping_house}")
        if self.shipping_apartment:
            address_parts.append(f"кв. {self.shipping_apartment}")
        if self.shipping_postal_code:
            address_parts.append(f"индекс: {self.shipping_postal_code}")
            
        return ", ".join(address_parts) if address_parts else "Адрес не указан"

class OrderItem(models.Model):
    """
    Модель позиции заказа.
    
    Attributes:
        order: Заказ, к которому относится позиция
        product: Товар в позиции
        quantity: Количество товара
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items", verbose_name="Товар")
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказов"
        
    @property
    def price(self) -> Decimal:
        """
        Вычисляет итоговую цену за позицию заказа с учетом скидки.
        
        Returns:
            Итоговая цена за позицию или 0, если товар не найден
        """
        if self.product:
            return self.product.get_discounted_price() * self.quantity
        return 0
        
    def __str__(self) -> str:
        """
        Строковое представление позиции заказа.
        
        Returns:
            Строка с информацией о товаре, количестве и номере заказа
        """
        return f"{self.product.name} x {self.quantity} в заказе №{self.order.id}"


class Review(models.Model):
    """
    Модель отзыва на товар.
    
    Attributes:
        user: Пользователь, оставивший отзыв
        product: Товар, на который оставлен отзыв
        rating: Рейтинг товара (от 1 до 5)
        comment: Комментарий к отзыву
        pros: Достоинства товара
        cons: Недостатки товара
        created_at: Дата создания отзыва
    """
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)] 

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews", verbose_name="Пользоваетль")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews", verbose_name="Товар")
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, default=5, verbose_name="Рейтинг")
    comment = models.TextField(blank=True, null=True, verbose_name="Отзыв")
    pros = models.TextField(blank=True, null=True, verbose_name="Плюсы")
    cons = models.TextField(blank=True, null=True, verbose_name="Минусы")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self) -> str:
        """
        Строковое представление отзыва.
        
        Returns:
            Строка с информацией о пользователе и рейтинге
        """
        return f"Отзыв от {self.user.username} - {self.rating}"

class Wishlist(models.Model):
    """
    Модель списка желаемых товаров пользователя.
    
    Attributes:
        user: Пользователь, добавивший товар в список желаемого
        product: Товар, добавленный в список желаемого
        added_at: Дата добавления товара в список
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist", verbose_name="Пользователь")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlisted_by", verbose_name="Продукт")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлен")

    class Meta:
        unique_together = ('user', 'product')
        verbose_name = "Список желаемого"
        verbose_name_plural = "Списки желаемого"

    def __str__(self) -> str:
        """
        Строковое представление элемента списка желаемого.
        
        Returns:
            Строка с информацией о пользователе и товаре
        """
        return f"{self.user.username} - {self.product.name}"

class PEExam(models.Model):
    """
    Модель для хранения информации о экзаменах.
    
    Attributes:
        name: Название экзамена
        created_at: Дата создания записи
        exam_date: Дата проведения экзамена
        image: Изображение к экзамену
        users: Пользователи, которые должны писать экзамен
        is_public: Статус публикации экзамена
    """
    name = models.CharField(max_length=255, verbose_name="Название экзамена")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    exam_date = models.DateTimeField(verbose_name="Дата проведения")
    image = models.ImageField(upload_to='exam_images/', blank=True, null=True, verbose_name="Изображение задания")
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="exams", verbose_name="Участники")
    is_public = models.BooleanField(default=False, verbose_name="Опубликовано")

    class Meta:
        verbose_name = "Экзамен"
        verbose_name_plural = "Экзамены"
        ordering = ['-exam_date']

    def __str__(self) -> str:
        """
        Строковое представление экзамена.
        
        Returns:
            Название экзамена
        """
        return self.name