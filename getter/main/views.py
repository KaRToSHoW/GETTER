from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.db import models
from django.db.models import Q, Avg, Count, Sum
from .models import Category, Product, Wishlist, Order, OrderItem, Review
from .serializers import CategorySerializer, ProductSerializer, OrderSerializer, OrderItemSerializer, ReviewSerializer, WishlistSerializer
from django.utils import timezone

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

    def patch(self, request, pk):
        if not request.user.is_superuser:
            return Response({'error': 'Только администратор может редактировать товары'}, 
                          status=status.HTTP_403_FORBIDDEN)
        try:
            product = Product.objects.get(id=pk)
            serializer = ProductSerializer(product, data=request.data, partial=True, context={'request': request})
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
            print(f"Delete review attempt - User: {request.user.username}, is_superuser: {request.user.is_superuser}")
            print(f"Looking for review with id: {review_id}, product_id: {product_id}")
            
            if request.user.is_superuser:
                print("User is superuser, attempting to delete any review")
                review = Review.objects.get(id=review_id, product_id=product_id)
            else:
                print("User is not superuser, attempting to delete own review")
                review = Review.objects.get(id=review_id, product_id=product_id, user=request.user)
            
            print(f"Found review: {review.id} by user {review.user.username}")
            review.delete()
            print("Review deleted successfully")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Review.DoesNotExist:
            print(f"Review not found with id {review_id}")
            return Response({'error': 'Отзыв не найден'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error deleting review: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_activity(request, user_id=None):
    """Получение активности пользователя"""
    try:
        # Определяем, чью активность запрашиваем
        target_user_id = user_id if user_id and request.user.is_superuser else request.user.id
        
        # Получаем заказы пользователя
        orders = Order.objects.filter(user_id=target_user_id).order_by('-created_at')
        recent_orders = orders.select_related('user')[:5]
        total_orders = orders.count()
        total_spent = orders.exclude(status='canceled').aggregate(Sum('total_price'))['total_price__sum'] or 0

        # Получаем отзывы пользователя
        reviews = Review.objects.filter(user_id=target_user_id).order_by('-created_at')
        recent_reviews = reviews.select_related('product', 'user')[:5]
        total_reviews = reviews.count()

        # Получаем избранные товары
        wishlist = Wishlist.objects.filter(user_id=target_user_id).order_by('-added_at')
        wishlist_items = wishlist.select_related('product')[:5]
        total_wishlist = wishlist.count()

        # Форматируем ответ
        response_data = {
            'totalOrders': total_orders,
            'totalReviews': total_reviews,
            'wishlistCount': total_wishlist,
            'totalSpent': float(total_spent),
            'recentOrders': [{
                'id': order.id,
                'order_number': order.order_number,
                'total_price': float(order.total_price),
                'status': order.status,
                'created_at': order.created_at
            } for order in recent_orders],
            'recentReviews': [{
                'id': review.id,
                'product': {
                    'id': review.product.id,
                    'name': review.product.name,
                },
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at,
                'pros': review.pros,
                'cons': review.cons
            } for review in recent_reviews],
            'wishlistItems': [{
                'id': item.id,
                'product': {
                    'id': item.product.id,
                    'name': item.product.name,
                    'price': float(item.product.price)
                },
                'added_at': item.added_at
            } for item in wishlist_items]
        }

        return Response(response_data)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def advanced_product_search(request):
    """
    Расширенный поиск и анализ товаров с поддержкой живого поиска
    """
    search_term = request.query_params.get('search', '').strip()
    min_price = request.query_params.get('min_price')
    max_price = request.query_params.get('max_price')
    category = request.query_params.get('category')
    
    products = Product.objects.all()
    
    if search_term:
        products = products.filter(
            Q(name__icontains=search_term) |
            Q(sku__contains=search_term) |
            Q(category__name__icontains=search_term)
        )
    
    if min_price:
        products = products.filter(price__gte=float(min_price))
    
    if max_price:
        products = products.filter(price__lte=float(max_price))
    
    if category:
        products = products.filter(category__name__icontains=category)

    # Добавляем аннотации и оптимизируем запрос
    products = products.select_related('category').annotate(
        average_rating=Avg('reviews__rating')
    )

    # Используем values() для оптимизации, если запрос из выпадающего списка
    if request.query_params.get('dropdown') == 'true':
        products = products.values(
            'id', 'name', 'price', 'image', 
            'category__name', 'is_available'
        )[:5]  # Ограничиваем результаты для выпадающего списка
        
        # Форматируем результаты
        results = [{
            'id': p['id'],
            'name': p['name'],
            'price': p['price'],
            'image': p['image'],
            'category': {'name': p['category__name']},
            'is_available': p['is_available']
        } for p in products]
        
        return Response({
            'products': results,
            'total': products.count()
        })

    # Полная сериализация для страницы поиска
    serializer = ProductSerializer(products, many=True, context={'request': request})
    
    return Response({
        'products': serializer.data,
        'total': products.count(),
        'query': search_term
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def new_products(request):
    """Получение новых товаров по дате создания"""
    # Получаем текущую дату
    current_date = timezone.now()
    
    # Определяем дату, которая была 30 дней назад
    month_ago = current_date - timezone.timedelta(days=30)
    
    # Найдем все товары, созданные за последние 30 дней
    new_products = Product.objects.filter(
        creation_date__gte=month_ago
    ).order_by('-creation_date')[:10]  # Сортируем по дате создания (от новых к старым)
    
    # Аннотируем средний рейтинг
    new_products = new_products.annotate(
        average_rating=Avg('reviews__rating')
    )
    
    serializer = ProductSerializer(new_products, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def popular_products(request):
    """Получение популярных товаров по количеству отзывов и рейтингу"""
    # Находим товары с наибольшим количеством отзывов и высоким рейтингом
    popular_products = Product.objects.annotate(
        reviews_count=Count('reviews'),
        average_rating=Avg('reviews__rating')
    ).filter(
        reviews_count__gt=0  # Только товары с отзывами
    ).order_by('-reviews_count', '-average_rating')[:10]
    
    serializer = ProductSerializer(popular_products, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def recent_reviews(request):
    """Получение последних отзывов пользователей"""
    # Получаем последние отзывы с информацией о продуктах и пользователях
    reviews = Review.objects.select_related('product', 'user').order_by('-created_at')[:10]
    
    # Создаем расширенный ответ
    response_data = []
    for review in reviews:
        review_data = {
            'id': review.id,
            'rating': review.rating,
            'comment': review.comment,
            'pros': review.pros,
            'cons': review.cons,
            'created_at': review.created_at,
            'product': {
                'id': review.product.id,
                'name': review.product.name,
                'image': review.product.image.url if review.product.image else None,
            },
            'user': {
                'id': review.user.id,
                'username': review.user.username,
                'profile_image': review.user.get_profile_image_url() if hasattr(review.user, 'get_profile_image_url') else None,
            }
        }
        response_data.append(review_data)
    
    return Response(response_data)