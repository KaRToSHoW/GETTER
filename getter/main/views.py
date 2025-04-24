from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from .models import Category, Product, Wishlist, Order, OrderItem, Review
from .serializers import CategorySerializer, ProductSerializer, OrderSerializer, OrderItemSerializer, ReviewSerializer
from django.db.models import Avg, Count, Sum

class CategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Аннотируем количество продуктов в каждой категории
        categories = Category.objects.annotate(product_count=Count('products'))
        serializer = CategorySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Только администратор может создавать категории'}, 
                          status=status.HTTP_403_FORBIDDEN)
        serializer = CategorySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Только администратор может редактировать категории'}, 
                          status=status.HTTP_403_FORBIDDEN)
        try:
            category_id = request.data.get('id')
            if not category_id:
                return Response({'error': 'ID категории не указан'}, status=status.HTTP_400_BAD_REQUEST)
            
            category = Category.objects.get(id=category_id)
            serializer = CategorySerializer(category, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Category.DoesNotExist:
            return Response({'error': 'Категория не найдена'}, status=status.HTTP_404_NOT_FOUND)

class ProductListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        category_id = request.query_params.get('category')
        if category_id:
            products = Product.objects.filter(category_id=category_id).select_related('category')
        else:
            products = Product.objects.all().select_related('category')

        # Аннотируем средний рейтинг
        products = products.annotate(average_rating=Avg('reviews__rating'))

        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Только администратор может создавать товары'}, 
                          status=status.HTTP_403_FORBIDDEN)
        try:
            serializer = ProductSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            product = Product.objects.select_related('category').prefetch_related('reviews__user').get(id=pk)
            serializer = ProductSerializer(product, context={'request': request})
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Продукт не найден'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        if not request.user.is_superuser:
            return Response({'error': 'Только администратор может удалять товары'}, 
                          status=status.HTTP_403_FORBIDDEN)
        try:
            product = Product.objects.get(id=pk)
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({'error': 'Продукт не найден'}, 
                          status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        if not request.user.is_superuser:
            return Response({'error': 'Только администратор может редактировать товары'}, 
                          status=status.HTTP_403_FORBIDDEN)
        try:
            product = Product.objects.get(id=pk)
            serializer = ProductSerializer(product, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response({'error': 'Продукт не найден'}, 
                          status=status.HTTP_404_NOT_FOUND)

class ReviewListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, product_id):
        reviews = Review.objects.filter(product_id=product_id)
        serializer = ReviewSerializer(reviews, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            # Добавляем product и user в контекст сериализатора
            serializer = ReviewSerializer(data={
                'rating': request.data.get('rating'),
                'comment': request.data.get('comment'),
                'pros': request.data.get('pros', ''),
                'cons': request.data.get('cons', '')
            }, context={
                'request': request,
                'product': product,
                'user': request.user
            })
            if serializer.is_valid():
                review = serializer.save()  # Сохраняем с уже установленным контекстом
                return Response(ReviewSerializer(review, context={'request': request}).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response({'error': 'Продукт не найден'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, product_id, review_id):
        try:
            review = Review.objects.get(id=review_id, product_id=product_id, user=request.user)
            review.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Review.DoesNotExist:
            return Response({'error': 'Отзыв не найден'}, status=status.HTTP_404_NOT_FOUND)

class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            order = Order.objects.get(id=pk, user=request.user)
            serializer = OrderSerializer(order, context={'request': request})
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({'error': 'Заказ не найден'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_wishlist(request):
    try:
        print("Полученные данные:", request.data)
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'error': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        product = Product.objects.get(id=product_id)
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        if created:
            return Response({'message': 'Товар добавлен в желаемое', 'in_wishlist': True}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Товар уже в списке желаемого', 'in_wishlist': True}, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response({'error': 'Продукт не найден'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print("Ошибка:", str(e))
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_wishlist(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()
        if wishlist_item:
            wishlist_item.delete()
            return Response({'message': 'Товар удален из желаемого', 'in_wishlist': False}, status=status.HTTP_200_OK)
        return Response({'message': 'Товар не найден в желаемом'}, status=status.HTTP_404_NOT_FOUND)
    except Product.DoesNotExist:
        return Response({'error': 'Продукт не найден'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print("Ошибка:", str(e))
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_wishlist(request):
    wishlist = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
    return Response({'wishlist': list(wishlist)})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(request):
    try:
        order = Order.objects.filter(user=request.user, status='pending').first()
        total_orders_sum = Order.objects.filter(user=request.user).aggregate(total_sum=Sum('total_price'))['total_sum'] or 0

        if not order:
            return Response({'items': [], 'total_price': float(0), 'total_orders_sum': float(total_orders_sum)}, status=status.HTTP_200_OK)
        
        serializer = OrderSerializer(order)
        data = serializer.data
        data['total_price'] = float(data['total_price'])
        data['total_orders_sum'] = float(total_orders_sum)
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    try:
        print("Полученные данные:", request.data)  # Лог входящих данных
        
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))  # Убедимся, что это число
        print(f"ID товара: {product_id}, Количество: {quantity}")

        if not product_id:
            print("Ошибка: product_id отсутствует")
            return Response({'error': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        product = Product.objects.get(id=product_id)
        print(f"Найден продукт: {product.name}, Остаток: {product.stock}")

        if product.stock < quantity:
            print("Ошибка: недостаточно товара на складе")
            return Response({'error': 'Недостаточно товара на складе'}, status=status.HTTP_400_BAD_REQUEST)

        order, created = Order.objects.get_or_create(user=request.user, status='pending')
        print(f"Текущий заказ: {order.id}, создан ли новый: {created}")

        order_item, created = OrderItem.objects.get_or_create(
        order=order,
        product=product,
        defaults={"quantity": quantity}  # Устанавливаем quantity сразу при создании
    )

        if not created:
            order_item.quantity += quantity  # Если уже есть, увеличиваем количество
            order_item.save()


        order.save()  # Пересчитываем total_price
        print(f"Итоговая сумма заказа: {order.total_price}")

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Product.DoesNotExist:
        print("Ошибка: Продукт не найден")
        return Response({'error': 'Продукт не найден'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        print("Ошибка:", str(e))  # Логируем любую другую ошибку
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, item_id):
    try:
        order_item = OrderItem.objects.get(id=item_id, order__user=request.user, order__status='pending')
        order = order_item.order
        order_item.delete()
        order.save()  # Пересчитывает total_price
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except OrderItem.DoesNotExist:
        return Response({'error': 'Позиция не найдена'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_favorites(request):
    """Получение всех избранных товаров пользователя"""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    products = [item.product for item in wishlist_items]
    
    # Аннотируем средний рейтинг
    product_ids = [product.id for product in products]
    products_with_rating = Product.objects.filter(id__in=product_ids).annotate(
        average_rating=Avg('reviews__rating'),
        reviews_count=Count('reviews')
    )
    
    # Создаем словарь для быстрого доступа к продуктам с рейтингом
    products_dict = {product.id: product for product in products_with_rating}
    
    # Заменяем продукты на аннотированные версии
    products_with_data = [products_dict.get(product.id, product) for product in products]
    
    serializer = ProductSerializer(products_with_data, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_orders(request):
    """Получение всех заказов пользователя"""
    # Используем related_name="orders" из модели Order для доступа к заказам пользователя
    user_orders = request.user.orders.all().order_by('-created_at')
    
    # Группируем заказы по статусу
    pending_orders = user_orders.filter(status='pending')
    completed_orders = user_orders.filter(status__in=['delivered', 'shipped'])
    canceled_orders = user_orders.filter(status='canceled')
    
    # Вычисляем общую сумму всех заказов
    total_spent = user_orders.exclude(status='canceled').aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Сериализуем каждую группу заказов
    pending_serializer = OrderSerializer(pending_orders, many=True, context={'request': request})
    completed_serializer = OrderSerializer(completed_orders, many=True, context={'request': request})
    canceled_serializer = OrderSerializer(canceled_orders, many=True, context={'request': request})
    
    return Response({
        'pending_orders': pending_serializer.data,
        'completed_orders': completed_serializer.data,
        'canceled_orders': canceled_serializer.data,
        'total_spent': float(total_spent)
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def popular_wishlist_products(request):
    """Получение популярных товаров из списков желаемого"""
    # Используем related_name="wishlisted_by" из модели Wishlist для определения популярных товаров
    popular_products = Product.objects.annotate(
        wishlist_count=Count('wishlisted_by')
    ).filter(
        wishlist_count__gt=0  # Только товары, добавленные хотя бы в один wishlist
    ).order_by('-wishlist_count')[:10]
    
    # Добавляем информацию о рейтинге
    popular_products = popular_products.annotate(
        average_rating=Avg('reviews__rating'),
        reviews_count=Count('reviews')
    )
    
    serializer = ProductSerializer(popular_products, many=True, context={'request': request})
    return Response(serializer.data)