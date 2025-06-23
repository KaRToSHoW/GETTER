# main/serializers.py
from rest_framework import serializers
from .models import Category, Product, Order, OrderItem, Review, Wishlist
from users.serializers import UserSerializer
from typing import Dict, Any, List, Optional, Union
from decimal import Decimal

class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category.
    
    Attributes:
        image: Поле изображения категории
        url: Вычисляемое поле для URL категории
        product_count: Поле для количества продуктов в категории
    """
    image = serializers.ImageField(required=False, allow_null=True)
    url = serializers.SerializerMethodField()
    product_count = serializers.IntegerField(read_only=True, required=False)  # Количество продуктов

    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'url', 'product_count']

    def get_url(self, obj: Category) -> str:
        """
        Получает URL для категории.
        
        Args:
            obj: Объект категории
            
        Returns:
            URL категории
        """
        return obj.get_absolute_url()

    def to_representation(self, instance: Category) -> Dict[str, Any]:
        """
        Преобразует объект категории в словарь для сериализации.
        Добавляет абсолютный URL для изображения.
        
        Args:
            instance: Объект категории
            
        Returns:
            Словарь с данными категории
        """
        representation = super().to_representation(instance)
        if instance.image:
            request = self.context.get('request')
            if request:
                representation['image'] = request.build_absolute_uri(instance.image.url)
        return representation
    
class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Product.
    
    Attributes:
        category: Вложенный сериализатор для категории товара
        category_id: ID категории (только для записи)
        image: Поле изображения товара
        documentation: Поле документации товара
        url: Вычисляемое поле для URL товара
        average_rating: Средний рейтинг товара
        discounted_price: Вычисляемое поле для цены со скидкой
    """
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    documentation = serializers.FileField(required=False, allow_null=True)
    url = serializers.SerializerMethodField()
    average_rating = serializers.FloatField(read_only=True, required=False)
    discounted_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'sku', 'name', 'description', 'price', 'discount', 'discounted_price', 
                 'stock', 'category', 'category_id', 'image', 'documentation', 'is_available', 
                 'specifications', 'url', 'average_rating', 'creation_date']

    def get_url(self, obj: Product) -> str:
        """
        Получает URL для товара.
        
        Args:
            obj: Объект товара
            
        Returns:
            URL товара
        """
        return obj.get_absolute_url()
        
    def get_discounted_price(self, obj: Product) -> float:
        """
        Получает цену товара с учетом скидки.
        
        Args:
            obj: Объект товара
            
        Returns:
            Цена товара со скидкой
        """
        return obj.get_discounted_price()

    def to_representation(self, instance: Product) -> Dict[str, Any]:
        """
        Преобразует объект товара в словарь для сериализации.
        Добавляет абсолютные URL для изображения и документации.
        
        Args:
            instance: Объект товара
            
        Returns:
            Словарь с данными товара
        """
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if request:
            if instance.image:
                representation['image'] = request.build_absolute_uri(instance.image.url)
            if instance.documentation:
                representation['documentation'] = request.build_absolute_uri(instance.documentation.url)
        return representation

class OrderItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели OrderItem.
    
    Attributes:
        product: Вложенный сериализатор для товара
        price: Вычисляемое поле для цены позиции заказа
    """
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    quantity = serializers.IntegerField(min_value=1)
    price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_id', 'quantity', 'price']

    def get_price(self, obj: OrderItem) -> float:
        """
        Вычисляет итоговую цену за позицию заказа с учетом скидки.
        
        Args:
            obj: Объект позиции заказа
            
        Returns:
            Итоговая цена за позицию заказа
        """
        if obj.product:
            return float(obj.product.get_discounted_price() * obj.quantity)
        return 0.0
    
    def validate(self, attrs):
        """
        Валидирует наличие товара на складе при создании или обновлении позиции заказа
        """
        product_id = attrs.get('product_id')
        quantity = attrs.get('quantity', 1)
        
        try:
            product = Product.objects.get(id=product_id)
            
            # Проверяем наличие товара на складе
            if quantity > product.stock:
                raise serializers.ValidationError({
                    'quantity': f'Недостаточно товара на складе. Доступно: {product.stock}'
                })
                
        except Product.DoesNotExist:
            raise serializers.ValidationError({
                'product_id': 'Указанный товар не найден'
            })
            
        return attrs

class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Order.
    
    Attributes:
        items: Вложенный сериализатор для позиций заказа
        user: Строковое представление пользователя
        url: Вычисляемое поле для URL заказа
        total_orders_sum: Сумма всех заказов пользователя
        shipping_address: Вычисляемое поле для полного адреса доставки
    """
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    url = serializers.SerializerMethodField()
    total_orders_sum = serializers.FloatField(read_only=True, required=False)  # Сумма всех заказов пользователя
    shipping_address = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_price', 'created_at', 'updated_at', 'order_number', 
                  'items', 'url', 'total_orders_sum', 'shipping_city', 'shipping_street', 
                  'shipping_house', 'shipping_apartment', 'shipping_postal_code', 
                  'shipping_comment', 'shipping_address']

    def get_url(self, obj: Order) -> str:
        """
        Получает URL для заказа.
        
        Args:
            obj: Объект заказа
            
        Returns:
            URL заказа
        """
        return obj.get_absolute_url()
        
    def get_shipping_address(self, obj: Order) -> str:
        """
        Получает полный адрес доставки.
        
        Args:
            obj: Объект заказа
            
        Returns:
            Строка с полным адресом доставки
        """
        return obj.get_shipping_address()
    
    def validate(self, attrs):
        """
        Валидирует данные заказа:
        - Проверяет обязательные поля адреса доставки
        - Проверяет формат почтового индекса
        - Проверяет минимальную и максимальную сумму заказа
        - Проверяет наличие товаров на складе
        """
        # Получаем текущий контекст - при создании, обновлении или без изменений
        is_create = self.instance is None
        is_update = self.instance is not None and attrs.get('status') == 'assembling'
        
        # Проверяем только при создании заказа или изменении статуса на "в сборке"
        if is_create or is_update:
            # Проверка адреса доставки
            shipping_city = attrs.get('shipping_city')
            shipping_street = attrs.get('shipping_street')
            shipping_house = attrs.get('shipping_house')
            shipping_postal_code = attrs.get('shipping_postal_code')
            
            # Проверка обязательных полей
            if not shipping_city:
                raise serializers.ValidationError({'shipping_city': 'Пожалуйста, укажите город'})
            
            if not shipping_street:
                raise serializers.ValidationError({'shipping_street': 'Пожалуйста, укажите улицу'})
                
            if not shipping_house:
                raise serializers.ValidationError({'shipping_house': 'Пожалуйста, укажите номер дома'})
            
            # Проверка формата города (только кириллические буквы)
            if shipping_city and not all(c.isalpha() or c.isspace() or c == '-' for c in shipping_city):
                raise serializers.ValidationError({
                    'shipping_city': 'Название города должно содержать только кириллические буквы'
                })
            
            # Проверка формата улицы
            if shipping_street and not all(c.isalnum() or c.isspace() or c in '.,/-' for c in shipping_street):
                raise serializers.ValidationError({
                    'shipping_street': 'Название улицы содержит недопустимые символы'
                })
            
            # Проверка формата номера дома
            if shipping_house and not all(c.isalnum() or c in '/-' for c in shipping_house):
                raise serializers.ValidationError({
                    'shipping_house': 'Недопустимый формат номера дома'
                })
            
            # Проверка почтового индекса (6 цифр для России)
            if shipping_postal_code:
                if not shipping_postal_code.isdigit() or len(shipping_postal_code) != 6:
                    raise serializers.ValidationError({
                        'shipping_postal_code': 'Почтовый индекс должен состоять из 6 цифр'
                    })
            
            # Проверка минимальной и максимальной суммы заказа
            MIN_ORDER_AMOUNT = Decimal('500.00')
            MAX_ORDER_AMOUNT = Decimal('100000.00')
            
            # Если это создание заказа или установка суммы вручную
            if is_create or 'total_price' in attrs:
                total_price = attrs.get('total_price')
                
                if total_price and total_price < MIN_ORDER_AMOUNT:
                    raise serializers.ValidationError({
                        'total_price': f'Минимальная сумма заказа составляет {MIN_ORDER_AMOUNT} ₽'
                    })
                
                if total_price and total_price > MAX_ORDER_AMOUNT:
                    raise serializers.ValidationError({
                        'total_price': f'Максимальная сумма заказа составляет {MAX_ORDER_AMOUNT} ₽'
                    })
            
            # Проверка наличия товаров на складе (только для экземпляра)
            if self.instance:
                for item in self.instance.items.all():
                    if item.quantity > item.product.stock:
                        raise serializers.ValidationError({
                            'items': f'Недостаточно товара "{item.product.name}" на складе. '
                                     f'Доступно: {item.product.stock}'
                        })
        
        return attrs

class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Review.
    
    Attributes:
        user: Вложенный сериализатор для пользователя
        product: Вложенный сериализатор для товара
    """
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Review
        fields = ['id', 'user', 'product', 'rating', 'comment', 'pros', 'cons', 'created_at']

    def validate(self, attrs):
        """
        Проверяет право пользователя оставлять отзыв на товар
        """
        # Получаем пользователя и товар из контекста
        user = self.context.get('user')
        product = self.context.get('product')
        
        if not product or not user:
            raise serializers.ValidationError("Product or user is missing in context")
        
        # Если пользователь администратор, он может оставлять отзывы на любой товар
        if user.is_superuser:
            return attrs
            
        # Проверяем, покупал ли пользователь данный товар
        from .models import OrderItem
        has_purchased = OrderItem.objects.filter(
            order__user=user,
            product=product,
            order__status__in=['shipped', 'delivered']  # Только доставленные или отправленные заказы
        ).exists()
        
        if not has_purchased:
            raise serializers.ValidationError(
                "Вы можете оставить отзыв только на приобретенный товар"
            )
            
        return attrs

    def create(self, validated_data: Dict[str, Any]) -> Review:
        """
        Создает новый отзыв.
        
        Args:
            validated_data: Проверенные данные для создания отзыва
            
        Returns:
            Созданный объект отзыва
            
        Raises:
            serializers.ValidationError: Если в контексте отсутствует продукт или пользователь
        """
        product = self.context.get('product')
        user = self.context.get('user')
        if not product or not user:
            raise serializers.ValidationError("Продукт или пользователь отсутствуют в контексте")
        review = Review.objects.create(
            product=product,
            user=user,
            rating=validated_data['rating'],
            comment=validated_data.get('comment', ''),
            pros=validated_data.get('pros', ''),
            cons=validated_data.get('cons', '')
        )
        return review

class WishlistSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Wishlist.
    
    Attributes:
        user: Строковое представление пользователя
        product: Вложенный сериализатор для товара
    """
    user = serializers.StringRelatedField(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'product', 'added_at']