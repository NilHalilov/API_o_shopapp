"""Модуль для описания кастомных разрешений для пользователя"""

from rest_framework.permissions import BasePermission


class IsCurrentUserProfileOrAdmin(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        return obj.user == request.user
