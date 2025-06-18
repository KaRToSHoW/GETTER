from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import User
from django.core import mail

class UserModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

    def test_user_creation(self):
        """Тест создания пользователя"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpassword123'))

    def test_get_profile_image_url(self):
        """Тест получения URL изображения профиля"""
        # Проверяем дефолтное изображение, когда нет загруженного
        self.assertTrue(self.user.get_profile_image_url().endswith('profile_images/default_profile_image.png'))

class UserAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword123'
        )
        self.register_url = reverse('register_api')
        self.profile_url = reverse('profile')
        self.upload_image_url = reverse('upload-profile-image')
        self.remove_image_url = reverse('remove-profile-image')
        self.test_email_url = reverse('test-email')

    def test_register_api(self):
        """Тест API регистрации пользователя"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_api_missing_fields(self):
        """Тест API регистрации с отсутствующими полями"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            # Отсутствует пароль
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_api_duplicate_username(self):
        """Тест API регистрации с существующим именем пользователя"""
        data = {
            'username': 'testuser',  # Уже существует
            'email': 'another@example.com',
            'password': 'newpassword123'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_get_unauthorized(self):
        """Тест получения профиля без авторизации"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_profile_get_authorized(self):
        """Тест получения профиля с авторизацией"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_profile_update(self):
        """Тест обновления профиля пользователя"""
        self.client.force_authenticate(user=self.user)
        data = {
            'first_name': 'Updated',
            'last_name': 'User'
        }
        response = self.client.put(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'User')

    def test_test_email_api(self):
        """Тест API отправки тестовых писем"""
        self.client.force_authenticate(user=self.user)
        data = {'email_type': 'welcome'}
        response = self.client.post(self.test_email_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)  # Проверяем, что письмо было отправлено
        self.assertIn('Добро пожаловать', mail.outbox[0].subject)
