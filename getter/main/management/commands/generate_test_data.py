from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from main.models import Product, Category, Order, OrderItem, Review, Wishlist
import random
import lorem
import string
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Генерирует тестовые данные для проверки задач Celery'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Начинаем генерацию тестовых данных для Celery-задач...'))
        
        # 1. Создание пользователей с разной активностью
        self.create_test_users()
        
        # 2. Создание категорий и товаров с разным наличием
        self.create_test_products()
        
        # 3. Создание заказов в разных статусах и с разными датами
        self.create_test_orders()
        
        # 4. Создание отзывов с разными датами
        self.create_test_reviews()
        
        self.stdout.write(self.style.SUCCESS('Генерация тестовых данных завершена!'))

    def create_test_users(self):
        """Создание пользователей с разными датами активности"""
        self.stdout.write(self.style.SUCCESS('Создание тестовых пользователей...'))
        
        # Активные пользователи (заходили недавно)
        for i in range(5):
            username = f'active_user_{i}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'active{i}@example.com',
                    password='testpass123'
                )
                # Последняя активность в течение последней недели
                days_ago = random.randint(1, 6)
                user.last_login = timezone.now() - timedelta(days=days_ago)
                user.save()
                self.stdout.write(f'Создан активный пользователь: {username}')
        
        # Неактивные пользователи (не заходили 30+ дней)
        for i in range(5):
            username = f'inactive_user_{i}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'inactive{i}@example.com',
                    password='testpass123'
                )
                # Последняя активность более 30 дней назад
                days_ago = random.randint(31, 60)
                user.last_login = timezone.now() - timedelta(days=days_ago)
                user.save()
                self.stdout.write(f'Создан неактивный пользователь: {username}')
        
        # Очень неактивные пользователи (не заходили 365+ дней)
        for i in range(3):
            username = f'very_inactive_user_{i}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'very_inactive{i}@example.com',
                    password='testpass123'
                )
                # Последняя активность более 365 дней назад
                days_ago = random.randint(366, 500)
                user.last_login = timezone.now() - timedelta(days=days_ago)
                user.save()
                self.stdout.write(f'Создан очень неактивный пользователь: {username}')

    def create_test_products(self):
        """Создание товаров с разным наличием"""
        self.stdout.write(self.style.SUCCESS('Создание тестовых товаров...'))
        
        # Создаем или получаем категории
        categories = []
        for name in ["Электроника", "Одежда", "Книги", "Мебель", "Инструменты"]:
            category, created = Category.objects.get_or_create(name=name)
            categories.append(category)
            status = "создана" if created else "уже существует"
            self.stdout.write(f'Категория {name} {status}')
        
        # Создаем товары с разным наличием
        # 1. Товары в наличии (stock > 0, is_available=True)
        for i in range(10):
            sku = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not Product.objects.filter(sku=sku).exists():
                product = Product.objects.create(
                    sku=sku,
                    name=f'Товар в наличии {i+1}',
                    description=lorem.paragraph(),
                    price=random.uniform(100, 10000),
                    stock=random.randint(1, 100),
                    category=random.choice(categories),
                    is_available=True,
                    specifications={"параметр": "значение"},
                    creation_date=timezone.now() - timedelta(days=random.randint(10, 100))
                )
                self.stdout.write(f'Создан товар в наличии: {product.name} (SKU: {sku}, stock: {product.stock})')
        
        # 2. Товары с нулевым наличием (stock = 0, is_available=True) - 
        # должны быть помечены как недоступные задачей update_product_availability
        for i in range(5):
            sku = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not Product.objects.filter(sku=sku).exists():
                product = Product.objects.create(
                    sku=sku,
                    name=f'Товар с нулевым наличием {i+1}',
                    description=lorem.paragraph(),
                    price=random.uniform(100, 10000),
                    stock=0,
                    category=random.choice(categories),
                    is_available=True,  # Специально устанавливаем True для проверки задачи
                    specifications={"параметр": "значение"},
                    creation_date=timezone.now() - timedelta(days=random.randint(10, 100))
                )
                self.stdout.write(f'Создан товар с нулевым наличием: {product.name} (SKU: {sku}, stock: 0)')
        
        # 3. Недоступные товары с наличием (stock > 0, is_available=False) - 
        # должны быть восстановлены задачей update_product_availability
        for i in range(5):
            sku = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not Product.objects.filter(sku=sku).exists():
                product = Product.objects.create(
                    sku=sku,
                    name=f'Недоступный товар с наличием {i+1}',
                    description=lorem.paragraph(),
                    price=random.uniform(100, 10000),
                    stock=random.randint(1, 100),
                    category=random.choice(categories),
                    is_available=False,  # Специально устанавливаем False для проверки задачи
                    specifications={"параметр": "значение"},
                    creation_date=timezone.now() - timedelta(days=random.randint(10, 100))
                )
                self.stdout.write(f'Создан недоступный товар с наличием: {product.name} (SKU: {sku}, stock: {product.stock})')

    def create_test_orders(self):
        """Создание заказов в разных статусах и с разными датами"""
        self.stdout.write(self.style.SUCCESS('Создание тестовых заказов...'))
        
        users = User.objects.all()[:10]  # Берем первых 10 пользователей
        products = Product.objects.filter(stock__gt=0)[:15]  # Берем первые 15 товаров в наличии
        
        if not users or not products:
            self.stdout.write(self.style.ERROR('Недостаточно пользователей или товаров для создания заказов'))
            return
        
        # 1. Создаем заказы в статусе "pending" с разными датами
        for i in range(3):
            # Заказ в статусе "pending" более 7 дней - должен быть отменен задачей
            user = random.choice(users)
            order = Order.objects.create(
                user=user,
                status='pending',
                created_at=timezone.now() - timedelta(days=random.randint(8, 14)),
                updated_at=timezone.now() - timedelta(days=random.randint(8, 14)),
            )
            
            # Добавляем позиции заказа
            for _ in range(random.randint(1, 3)):
                product = random.choice(products)
                quantity = random.randint(1, 5)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity
                )
            
            # Обновляем общую стоимость
            order.save()  # Вызовет метод save, который обновит total_price
            self.stdout.write(f'Создан заказ в статусе "pending" с датой {order.created_at.date()}, ID: {order.id}')
        
        # 2. Создаем заказы в статусе "shipped" с разными датами
        for i in range(3):
            # Заказ в статусе "shipped" более 3 дней - должен быть помечен как доставленный задачей
            user = random.choice(users)
            order = Order.objects.create(
                user=user,
                status='shipped',
                created_at=timezone.now() - timedelta(days=random.randint(10, 20)),
                updated_at=timezone.now() - timedelta(days=random.randint(4, 10)),  # Отправлен 4-10 дней назад
            )
            
            # Добавляем позиции заказа
            for _ in range(random.randint(1, 3)):
                product = random.choice(products)
                quantity = random.randint(1, 5)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity
                )
            
            # Обновляем общую стоимость
            order.save()  # Вызовет метод save, который обновит total_price
            self.stdout.write(f'Создан заказ в статусе "shipped" с датой обновления {order.updated_at.date()}, ID: {order.id}')
        
        # 3. Создаем обычные заказы в других статусах для полноты данных
        statuses = ['assembling', 'delivered', 'canceled']
        for status in statuses:
            for i in range(2):
                user = random.choice(users)
                order = Order.objects.create(
                    user=user,
                    status=status,
                    created_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                    updated_at=timezone.now() - timedelta(days=random.randint(0, 5)),
                )
                
                # Добавляем позиции заказа
                for _ in range(random.randint(1, 3)):
                    product = random.choice(products)
                    quantity = random.randint(1, 5)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity
                    )
                
                # Обновляем общую стоимость
                order.save()  # Вызовет метод save, который обновит total_price
                self.stdout.write(f'Создан заказ в статусе "{status}", ID: {order.id}')

    def create_test_reviews(self):
        """Создание отзывов с разными датами и рейтингами"""
        self.stdout.write(self.style.SUCCESS('Создание тестовых отзывов...'))
        
        users = User.objects.all()[:10]  # Берем первых 10 пользователей
        products = Product.objects.all()[:15]  # Берем первые 15 товаров
        
        if not users or not products:
            self.stdout.write(self.style.ERROR('Недостаточно пользователей или товаров для создания отзывов'))
            return
        
        # 1. Создаем обычные отзывы с комментариями и недавними датами
        for i in range(15):
            user = random.choice(users)
            product = random.choice(products)
            
            # Проверяем, нет ли уже отзыва от этого пользователя на этот товар
            if not Review.objects.filter(user=user, product=product).exists():
                review = Review.objects.create(
                    user=user,
                    product=product,
                    rating=random.randint(3, 5),
                    comment=lorem.paragraph(),
                    pros=lorem.sentence(),
                    cons=lorem.sentence(),
                    created_at=timezone.now() - timedelta(days=random.randint(1, 30))
                )
                self.stdout.write(f'Создан отзыв от {user.username} на товар {product.name}, рейтинг: {review.rating}')
        
        # 2. Создаем старые отзывы без комментариев (должны быть удалены задачей clean_old_reviews)
        for i in range(5):
            user = random.choice(users)
            product = random.choice(products)
            
            # Проверяем, нет ли уже отзыва от этого пользователя на этот товар
            if not Review.objects.filter(user=user, product=product).exists():
                review = Review.objects.create(
                    user=user,
                    product=product,
                    rating=random.randint(1, 5),
                    comment=None,  # Без комментария
                    pros=None,
                    cons=None,
                    created_at=timezone.now() - timedelta(days=random.randint(366, 500))  # Старше 1 года
                )
                self.stdout.write(f'Создан старый отзыв без комментария от {user.username} на товар {product.name}, рейтинг: {review.rating}')
        
        # 3. Создаем старые отзывы с комментариями (не должны быть удалены)
        for i in range(5):
            user = random.choice(users)
            product = random.choice(products)
            
            # Проверяем, нет ли уже отзыва от этого пользователя на этот товар
            if not Review.objects.filter(user=user, product=product).exists():
                review = Review.objects.create(
                    user=user,
                    product=product,
                    rating=random.randint(1, 5),
                    comment=lorem.paragraph(),  # С комментарием
                    pros=lorem.sentence(),
                    cons=lorem.sentence(),
                    created_at=timezone.now() - timedelta(days=random.randint(366, 500))  # Старше 1 года
                )
                self.stdout.write(f'Создан старый отзыв с комментарием от {user.username} на товар {product.name}, рейтинг: {review.rating}') 