from rest_framework import permissions

class IsAdminOrSelf(permissions.BasePermission):
    """
    Разрешение для доступа к данным пользователя.
    Разрешает доступ только администраторам и самому пользователю.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        # Разрешаем доступ если пользователь является администратором
        if request.user.is_superuser:
            return True
        # Разрешаем доступ если пользователь просматривает свои данные
        return obj.id == request.user.id