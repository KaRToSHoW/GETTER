from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from .permissions import IsAdminOrSelf
from .utils import send_welcome_email, send_password_reset_email, send_order_confirmation_email

from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from typing import List, Dict, Any, Union, Optional, Type
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
import requests
from rest_framework_simplejwt.tokens import RefreshToken

class UserViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для модели User.
    
    Обеспечивает CRUD операции для пользователей с проверкой прав доступа.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrSelf]  # Используем новое разрешение

    def get_permissions(self) -> List[BasePermission]:
        """
        Возвращает список разрешений в зависимости от действия.
        
        Для создания пользователя (регистрации) разрешаем доступ всем.
        Для остальных действий используем стандартные разрешения.
        
        Returns:
            Список объектов разрешений
        """
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

@api_view(['POST'])
def register_api(request: Request) -> Response:
    """
    API для регистрации нового пользователя.
    
    Args:
        request: Объект запроса с данными пользователя
        
    Returns:
        Response с сообщением об успешной регистрации или ошибке
    """
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not email or not password:
        return Response({'error': 'Заполните все поля'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Такой пользователь уже существует'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password)
    return Response({'message': 'Регистрация успешна!'}, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request: Request) -> Response:
    """
    Обработка GET и PUT запросов для профиля пользователя.
    
    GET: Возвращает данные профиля текущего пользователя.
    PUT: Обновляет данные профиля текущего пользователя.
    
    Args:
        request: Объект запроса
        
    Returns:
        Response с данными профиля или результатом обновления
    """
    user = request.user

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_profile_image(request: Request) -> Response:
    """
    Загрузка изображения профиля пользователя.
    
    Args:
        request: Объект запроса с файлом изображения
        
    Returns:
        Response с сообщением об успешной загрузке или ошибке
    """
    if 'profile_image' not in request.FILES:
        return Response({'error': 'Изображение не загружено'}, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    user.profile_image = request.FILES['profile_image']
    user.save()

    return Response({
        'message': 'Изображение успешно загружено',
        'profile_image': user.get_profile_image_url()
    }, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_profile_image(request: Request) -> Response:
    """
    Удаление изображения профиля пользователя.
    
    Args:
        request: Объект запроса
        
    Returns:
        Response с сообщением об успешном удалении или ошибке
    """
    user = request.user
    if user.profile_image:
        user.profile_image.delete()  # Удаляем файл с диска
        user.profile_image = None
        user.save()
        return Response({'message': 'Изображение успешно удалено'}, status=status.HTTP_200_OK)
    return Response({'error': 'Изображение не найдено'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_email(request: Request) -> Response:
    """
    Тестовый API-эндпоинт для отправки различных типов писем
    
    Args:
        request: Объект запроса с типом письма
        
    Returns:
        Response с сообщением об успешной отправке или ошибке
    """
    email_type = request.data.get('email_type', 'welcome')
    user_email = request.user.email
    
    if not user_email:
        return Response({'error': 'У вашего аккаунта не указан email адрес'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        if email_type == 'welcome':
            send_welcome_email(user_email)
            message = 'Приветственное письмо отправлено'
        elif email_type == 'password_reset':
            reset_link = f"http://localhost:8080/reset-password/?token=test_token_{request.user.id}"
            send_password_reset_email(user_email, reset_link)
            message = 'Письмо для сброса пароля отправлено'
        elif email_type == 'order':
            order_details = """
            Товар 1 - 2 шт. - 1000 руб.
            Товар 2 - 1 шт. - 500 руб.
            Итого: 1500 руб.
            """
            send_order_confirmation_email(user_email, "12345", order_details)
            message = 'Письмо с подтверждением заказа отправлено'
        else:
            return Response({'error': 'Неизвестный тип письма'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': message}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': f'Ошибка при отправке письма: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class YandexLoginView(APIView):
    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Missing token'}, status=400)

        yandex_response = requests.get(
            'https://login.yandex.ru/info',
            headers={'Authorization': f'OAuth {token}'}
        )

        if yandex_response.status_code != 200:
            return Response({'error': 'Invalid token'}, status=400)

        data = yandex_response.json()
        email = data.get('default_email')
        login = data.get('login')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        display_name = data.get('display_name')
        avatar_id = data.get('default_avatar_id')
        
        # Формируем URL аватара Яндекса, если он есть
        avatar_url = None
        if avatar_id and not data.get('is_avatar_empty', True):
            avatar_url = f"https://avatars.yandex.net/get-yapic/{avatar_id}/islands-200"
        
        # Для отладки выводим полученные данные
        print(f"Yandex data: {data}")
        if avatar_url:
            print(f"Avatar URL: {avatar_url}")

        if not email:
            return Response({'error': 'Email not provided'}, status=400)

        # Проверяем, существует ли пользователь с таким email
        user_exists = User.objects.filter(email=email).exists()
        
        if user_exists:
            user = User.objects.get(email=email)
            # Обновляем данные пользователя, если они изменились
            if first_name and user.first_name != first_name:
                user.first_name = first_name
            if last_name and user.last_name != last_name:
                user.last_name = last_name
            
            # Если у пользователя нет аватара и есть аватар Яндекса, загружаем его
            if avatar_url and not user.profile_image:
                try:
                    # Загружаем изображение с Яндекса
                    avatar_response = requests.get(avatar_url)
                    if avatar_response.status_code == 200:
                        from django.core.files.base import ContentFile
                        from io import BytesIO
                        import uuid
                        
                        # Генерируем уникальное имя файла
                        file_name = f"yandex_avatar_{uuid.uuid4()}.jpg"
                        
                        # Сохраняем изображение в профиль пользователя
                        user.profile_image.save(
                            file_name,
                            ContentFile(avatar_response.content),
                            save=True
                        )
                        print(f"Avatar saved for user {user.username}")
                except Exception as e:
                    print(f"Error saving avatar: {str(e)}")
            
            user.save()
        else:
            # Создаем нового пользователя с данными из Яндекса
            user = User.objects.create_user(
                username=login,
                email=email,
                password=None,  # Пароль не нужен для OAuth авторизации
                first_name=first_name or '',
                last_name=last_name or ''
            )
            
            # Если есть аватар Яндекса, загружаем его для нового пользователя
            if avatar_url:
                try:
                    # Загружаем изображение с Яндекса
                    avatar_response = requests.get(avatar_url)
                    if avatar_response.status_code == 200:
                        from django.core.files.base import ContentFile
                        from io import BytesIO
                        import uuid
                        
                        # Генерируем уникальное имя файла
                        file_name = f"yandex_avatar_{uuid.uuid4()}.jpg"
                        
                        # Сохраняем изображение в профиль пользователя
                        user.profile_image.save(
                            file_name,
                            ContentFile(avatar_response.content),
                            save=True
                        )
                        print(f"Avatar saved for new user {user.username}")
                except Exception as e:
                    print(f"Error saving avatar for new user: {str(e)}")

        refresh = RefreshToken.for_user(user)
        return Response({
            'token': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_superuser': user.is_superuser,
                'profile_image': user.get_profile_image_url() if hasattr(user, 'get_profile_image_url') else None,
                'yandex_avatar_url': avatar_url
            }
        })