# main/serializers.py
from rest_framework import serializers
from .models import Category, Product, Order, OrderItem, Review, Wishlist
from users.serializers import UserSerializer
from typing import Dict, Any, List, Optional, Union

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
    price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'price']

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

class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Review.
    
    Attributes:
        user: Вложенный сериализатор для пользователя
        product: Вложенный сериализатор для товара
    """
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'product', 'rating', 'comment', 'pros', 'cons', 'created_at']

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
            raise serializers.ValidationError("Product or user is missing in context")
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