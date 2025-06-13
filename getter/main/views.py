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
import random
from decimal import Decimal

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
        # Проверяем, есть ли у пользователя несколько корзин
        pending_orders = Order.objects.filter(user=request.user, status='pending')
        if pending_orders.count() > 1:
            # Если их несколько, оставляем только самую последнюю, остальные удаляем
            latest_order = pending_orders.order_by('-created_at').first()
            pending_orders.exclude(id=latest_order.id).delete()
            print(f"Удалены лишние корзины, оставлена корзина с ID: {latest_order.id}")
            order = latest_order
        else:
            order = pending_orders.first()

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

        # Проверяем, есть ли у пользователя несколько корзин (заказов со статусом pending)
        pending_orders = Order.objects.filter(user=request.user, status='pending')
        if pending_orders.count() > 1:
            # Если их несколько, оставляем только самую последнюю, остальные удаляем
            latest_order = pending_orders.order_by('-created_at').first()
            pending_orders.exclude(id=latest_order.id).delete()
            print(f"Удалены лишние корзины, оставлена корзина с ID: {latest_order.id}")
            order = latest_order
        else:
            # Если корзины нет или она одна, используем стандартную логику
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
        # Проверяем, есть ли у пользователя несколько корзин
        pending_orders = Order.objects.filter(user=request.user, status='pending')
        if pending_orders.count() > 1:
            # Если их несколько, оставляем только самую последнюю, остальные удаляем
            latest_order = pending_orders.order_by('-created_at').first()
            pending_orders.exclude(id=latest_order.id).delete()
            print(f"Удалены лишние корзины, оставлена корзина с ID: {latest_order.id}")
        
        # Пытаемся найти товар в корзине
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """Создание заказа из корзины"""
    try:
        print("=== Начало создания заказа ===")
        print(f"Пользователь: {request.user.username} (ID: {request.user.id})")
        
        # Проверяем, есть ли у пользователя несколько корзин
        pending_orders = Order.objects.filter(user=request.user, status='pending')
        print(f"Найдено корзин: {pending_orders.count()}")
        
        if pending_orders.count() > 1:
            # Если их несколько, оставляем только самую последнюю, остальные удаляем
            latest_order = pending_orders.order_by('-created_at').first()
            pending_orders.exclude(id=latest_order.id).delete()
            print(f"Удалены лишние корзины, оставлена корзина с ID: {latest_order.id}")
            cart = latest_order
        else:
            cart = pending_orders.first()
            print(f"Использована существующая корзина с ID: {cart.id if cart else 'Нет'}")
        
        if not cart:
            print("Ошибка: Корзина не найдена")
            return Response({'error': 'Корзина не найдена'}, status=status.HTTP_400_BAD_REQUEST)
            
        if not cart.items.exists():
            print("Ошибка: Корзина пуста")
            return Response({'error': 'Корзина пуста'}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"Корзина содержит {cart.items.count()} товаров")
        
        # Проверяем доступность всех товаров
        for item in cart.items.all():
            print(f"Проверка товара: {item.product.name} (ID: {item.product.id})")
            print(f"Количество в корзине: {item.quantity}, На складе: {item.product.stock}")
            
            if item.quantity > item.product.stock:
                error_msg = f'Недостаточно товара "{item.product.name}" на складе. Доступно: {item.product.stock}'
                print(f"Ошибка: {error_msg}")
                return Response({
                    'error': error_msg
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Обновляем статус заказа на "в сборке"
        print("Обновляем статус заказа на 'в сборке'")
        cart.status = 'assembling'
        
        # Получение и сохранение данных доставки из запроса
        print("Получение данных доставки из запроса:")
        shipping_data = request.data.get('shipping', {})
        cart.shipping_city = shipping_data.get('city')
        cart.shipping_street = shipping_data.get('street')
        cart.shipping_house = shipping_data.get('house')
        cart.shipping_apartment = shipping_data.get('apartment')
        cart.shipping_postal_code = shipping_data.get('postal_code')
        cart.shipping_comment = shipping_data.get('comment')
        
        print(f"Адрес доставки: {cart.get_shipping_address()}")
        
        # Генерируем номер заказа, если его нет
        if not cart.order_number:
            # Генерируем уникальный номер заказа
            timestamp = timezone.now().strftime('%Y%m%d%H%M')
            random_suffix = ''.join([str(random.randint(0, 9)) for _ in range(4)])
            cart.order_number = f"ORD-{timestamp}-{random_suffix}"
            print(f"Сгенерирован номер заказа: {cart.order_number}")
        
        # Вычисляем итоговую сумму заказа
        total_price = Decimal('0.00')
        print("Расчет итоговой суммы заказа:")
        for item in cart.items.all():
            # Используем метод get_discounted_price для учета скидки
            item_price = item.product.get_discounted_price() * item.quantity
            print(f"Товар: {item.product.name}, Количество: {item.quantity}, Цена за ед.: {item.product.get_discounted_price()} (скидка {item.product.discount}%), Итого: {item_price}")
            total_price += item_price
            
        print(f"Итоговая сумма заказа: {total_price}")
        cart.total_price = total_price
        
        # Сохраняем изменения в заказе
        try:
            cart.save()
            print(f"Заказ сохранен с ID: {cart.id}, статус: {cart.status}, сумма: {cart.total_price}")
        except Exception as save_error:
            print(f"Ошибка при сохранении заказа: {str(save_error)}")
            return Response({'error': f'Ошибка при сохранении заказа: {str(save_error)}'}, 
                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Обновляем количество товаров на складе
        print("Обновляем количество товаров на складе:")
        for item in cart.items.all():
            try:
                product = item.product
                old_stock = product.stock
                product.stock -= item.quantity
                print(f"Товар: {product.name}, Было: {old_stock}, Стало: {product.stock}")
                
                if product.stock <= 0:
                    product.is_available = False
                    print(f"Товар {product.name} помечен как недоступный")
                    
                product.save()
            except Exception as product_error:
                print(f"Ошибка при обновлении товара {item.product.name}: {str(product_error)}")
                # Продолжаем выполнение, не прерываем процесс
        
        # Создаем новую пустую корзину для пользователя
        try:
            new_cart = Order.objects.create(user=request.user, status='pending')
            print(f"Создана новая пустая корзина с ID: {new_cart.id}")
        except Exception as cart_error:
            print(f"Ошибка при создании новой корзины: {str(cart_error)}")
            # Не прерываем выполнение, это некритичная ошибка
        
        response_data = {
            'message': 'Заказ успешно создан',
            'order_id': cart.id,
            'order_number': cart.order_number,
            'total_price': float(cart.total_price),
            'shipping_address': cart.get_shipping_address()
        }
        print("=== Заказ успешно создан ===")
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"=== ОШИБКА: {str(e)} ===")
        import traceback
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_orders(request):
    """Получение всех заказов пользователя с полной информацией"""
    try:
        # Получаем все заказы пользователя, кроме корзины
        user_orders = Order.objects.filter(
            user=request.user
        ).exclude(
            status='pending'
        ).order_by('-created_at')
        
        # Группируем заказы по статусу
        pending_orders = user_orders.filter(status__in=['assembling'])
        completed_orders = user_orders.filter(status__in=['delivered', 'shipped'])
        canceled_orders = user_orders.filter(status='canceled')
        
        # Вычисляем общую сумму всех заказов
        total_spent = user_orders.exclude(status='canceled').aggregate(Sum('total_price'))['total_price__sum'] or 0
        
        # Подготавливаем детальную информацию о заказах
        orders_data = []
        for order in user_orders:
            order_items = []
            for item in order.items.all().select_related('product'):
                order_items.append({
                    'id': item.id,
                    'name': item.product.name,
                    'price': float(item.product.price),
                    'quantity': item.quantity,
                    'image': item.product.image.url if item.product.image else None,
                    'product_id': item.product.id
                })
            
            orders_data.append({
                'id': order.id,
                'number': order.order_number,
                'date': order.created_at,
                'status': order.status,
                'total': float(order.total_price),
                'items': order_items
            })
        
        return Response({
            'orders': orders_data,
            'pending_orders': OrderSerializer(pending_orders, many=True).data,
            'completed_orders': OrderSerializer(completed_orders, many=True).data,
            'canceled_orders': OrderSerializer(canceled_orders, many=True).data,
            'total_spent': float(total_spent)
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_user_purchased_product(request, product_id):
    """Проверяет, покупал ли пользователь данный товар"""
    try:
        # Если пользователь администратор, он может оставлять отзывы на любой товар
        if request.user.is_superuser:
            return Response({'purchased': True})
            
        # Более точная проверка через модель OrderItem
        has_purchased = OrderItem.objects.filter(
            order__user=request.user,
            product_id=product_id
        ).exists()
        
        # Дополнительная проверка для отладки
        if not has_purchased:
            # Проверим все заказы пользователя
            user_orders = Order.objects.filter(user=request.user).values_list('id', flat=True)
            # Проверим наличие данного товара в позициях заказа
            order_items = OrderItem.objects.filter(
                order_id__in=user_orders,
                product_id=product_id
            )
            
            if order_items.exists():
                # Если товар найден в заказах, разрешим оставить отзыв
                has_purchased = True
        
        # Отправим отладочную информацию
        return Response({
            'purchased': has_purchased,
            'user_id': request.user.id,
            'product_id': product_id,
            'debug': 'Заказ найден' if has_purchased else 'Заказ не найден'
        })
    except Exception as e:
        return Response({
            'error': str(e),
            'user_id': request.user.id,
            'product_id': product_id
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)