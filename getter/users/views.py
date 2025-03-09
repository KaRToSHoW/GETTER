from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User

from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # Только авторизованные пользователи могут делать запросы

@api_view(['POST'])
def register_api(request):
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
def profile(request):
    """ Обработка GET и PUT запросов для профиля пользователя """
    user = request.user

    if request.method == 'GET':
        profile_data = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'profile_image': user.get_profile_image_url() if user.profile_image else None,
        }
        return Response(profile_data)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_profile_image(request):
    """ Загрузка изображения профиля """
    if 'profile_image' not in request.FILES:
        return Response({'error': 'Изображение не загружено'}, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    user.profile_image = request.FILES['profile_image']
    user.save()

    return Response({
        'message': 'Изображение успешно загружено',
        'profile_image': user.get_profile_image_url()
    }, status=status.HTTP_200_OK)
    
# your_app/views.py
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_profile_image(request):
    """ Удаление изображения профиля """
    user = request.user
    if user.profile_image:
        user.profile_image.delete()  # Удаляем файл с диска
        user.profile_image = None
        user.save()
        return Response({'message': 'Изображение успешно удалено'}, status=status.HTTP_200_OK)
    return Response({'error': 'Изображение не найдено'}, status=status.HTTP_400_BAD_REQUEST)