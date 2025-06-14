from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView
from typing import Any, Union
from .models import User

class IsAdminOrSelf(permissions.BasePermission):
    """
    Разрешение для доступа к данным пользователя.
    Разрешает доступ только администраторам и самому пользователю.
    """
    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Проверяет, имеет ли пользователь разрешение на доступ к представлению.
        
        Args:
            request: Объект запроса
            view: Объект представления
            
        Returns:
            True, если пользователь аутентифицирован, иначе False
        """
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """
        Проверяет, имеет ли пользователь разрешение на доступ к объекту.
        
        Args:
            request: Объект запроса
            view: Объект представления
            obj: Объект, к которому запрашивается доступ
            
        Returns:
            True, если пользователь является администратором или объектом является сам пользователь,
            иначе False
        """
        # Разрешаем доступ если пользователь является администратором
        if request.user.is_superuser:
            return True
        # Разрешаем доступ если пользователь просматривает свои данные
        return obj.id == request.user.id