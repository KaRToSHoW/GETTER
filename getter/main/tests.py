from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from decimal import Decimal
from .models import Category, Product, Order, OrderItem, Review
from users.models import User

class CategoryModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Тестовая категория')

    def test_category_creation(self):
        """Тест создания категории"""
        self.assertEqual(self.category.name, 'Тестовая категория')
        self.assertEqual(str(self.category), 'Тестовая категория')

    def test_category_get_absolute_url(self):
        """Тест получения URL категории"""
        self.assertEqual(self.category.get_absolute_url(), reverse('category-list'))

class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Тестовая категория')
        self.product = Product.objects.create(
            sku='TEST001',
            name='Тестовый продукт',
            description='Описание тестового продукта',
            price=Decimal('100.00'),
            discount=10,
            stock=50,
            category=self.category
        )

    def test_product_creation(self):
        """Тест создания продукта"""
        self.assertEqual(self.product.name, 'Тестовый продукт')
        self.assertEqual(self.product.sku, 'TEST001')
        self.assertEqual(self.product.price, Decimal('100.00'))
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(str(self.product), 'Тестовый продукт')

    def test_product_get_discounted_price(self):
        """Тест расчета цены со скидкой"""
        # Проверяем продукт с 10% скидкой
        self.assertEqual(self.product.get_discounted_price(), Decimal('90.00'))
        
        # Проверяем продукт без скидки
        self.product.discount = 0
        self.product.save()
        self.assertEqual(self.product.get_discounted_price(), Decimal('100.00'))

class OrderModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.category = Category.objects.create(name='Тестовая категория')
        self.product1 = Product.objects.create(
            sku='TEST001',
            name='Тестовый продукт 1',
            price=Decimal('100.00'),
            discount=10,
            stock=50,
            category=self.category
        )
        self.product2 = Product.objects.create(
            sku='TEST002',
            name='Тестовый продукт 2',
            price=Decimal('200.00'),
            discount=0,
            stock=30,
            category=self.category
        )
        self.order = Order.objects.create(
            user=self.user,
            status='pending',
            shipping_city='Москва',
            shipping_street='Тестовая',
            shipping_house='1',
            shipping_apartment='101'
        )
        self.order_item1 = OrderItem.objects.create(
            order=self.order,
            product=self.product1,
            quantity=2
        )
        self.order_item2 = OrderItem.objects.create(
            order=self.order,
            product=self.product2,
            quantity=1
        )

    def test_order_creation(self):
        """Тест создания заказа"""
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.status, 'pending')
        self.assertEqual(self.order.items.count(), 2)

    def test_order_calculate_total_price(self):
        """Тест расчета общей стоимости заказа"""
        # Проверяем расчет: (100 - 10%) * 2 + 200 * 1 = 90 * 2 + 200 = 180 + 200 = 380
        total_price = self.order.calculate_total_price()
        self.assertEqual(total_price, Decimal('380.00'))

    def test_order_get_shipping_address(self):
        """Тест получения адреса доставки"""
        expected_address = "Москва, Тестовая, дом 1, кв. 101"
        self.assertEqual(self.order.get_shipping_address(), expected_address)

    def test_order_manager_pending(self):
        """Тест менеджера заказов для получения заказов в ожидании"""
        # Создаем еще один заказ со статусом 'shipped'
        order2 = Order.objects.create(
            user=self.user,
            status='shipped'
        )
        
        # Проверяем, что метод pending возвращает только заказы в статусе 'pending'
        pending_orders = Order.objects.pending()
        self.assertEqual(pending_orders.count(), 1)
        self.assertEqual(pending_orders.first(), self.order)

class ReviewModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.category = Category.objects.create(name='Тестовая категория')
        self.product = Product.objects.create(
            sku='TEST001',
            name='Тестовый продукт',
            price=Decimal('100.00'),
            stock=50,
            category=self.category
        )
        self.review = Review.objects.create(
            user=self.user,
            product=self.product,
            rating=4,
            comment='Хороший продукт',
            pros='Качественный, удобный',
            cons='Дороговато'
        )

    def test_review_creation(self):
        """Тест создания отзыва"""
        self.assertEqual(self.review.user, self.user)
        self.assertEqual(self.review.product, self.product)
        self.assertEqual(self.review.rating, 4)
        self.assertEqual(self.review.comment, 'Хороший продукт')

class ProductAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.category = Category.objects.create(name='Тестовая категория')
        self.product = Product.objects.create(
            sku='TEST001',
            name='Тестовый продукт',
            description='Описание тестового продукта',
            price=Decimal('100.00'),
            discount=10,
            stock=50,
            category=self.category
        )
        self.product_list_url = reverse('product-list')
        self.product_detail_url = reverse('product-detail', kwargs={'pk': self.product.pk})

    def test_product_list(self):
        """Тест получения списка продуктов"""
        response = self.client.get(self.product_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        product_names = [p['name'] for p in response.data]
        self.assertIn('Тестовый продукт', product_names)

    def test_product_detail(self):
        """Тест получения детальной информации о продукте"""
        response = self.client.get(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Тестовый продукт')
        self.assertEqual(response.data['price'], '100.00')
        self.assertEqual(response.data['discount'], 10)
