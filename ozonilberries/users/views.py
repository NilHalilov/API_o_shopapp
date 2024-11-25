"""Модуль для описания представлений для модели 'Profile'"""

import os

from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from users.models import Profile
from users.permissions import IsCurrentUserProfileOrAdmin
from users.serializers import (
    ProfileAvatarSerializer,
    ProfilePasswordSerializer,
    ProfileSerializer,
)


@extend_schema_view(
    create=extend_schema(
        tags=["profile"],
        summary="Обновить собственный профиль",
        description="Update user profile",
    ),
    password=extend_schema(
        tags=["profile"],
        summary="Изменить пароль",
        description="Update user password",
    ),
    avatar=extend_schema(
        tags=["profile"],
        summary="Изменить аватарку",
        description="Update user avatar",
    ),
)
class ProfileViewSet(CreateModelMixin, GenericViewSet):
    """ViewSet для работы с моделью `Profile`"""

    queryset = Profile.objects.all()
    permission_classes = (IsCurrentUserProfileOrAdmin,)

    def get_serializer_class(self):
        if self.action == "create":
            return ProfileSerializer
        elif self.action == "password":
            return ProfilePasswordSerializer
        elif self.action == "avatar":
            return ProfileAvatarSerializer

    @action(detail=False, methods=["post"])
    def password(self, request):
        """Метод для смены пароля"""
        user_profile = Profile.objects.get(user=request.user)
        self.check_object_permissions(request, user_profile)

        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if user.check_password(serializer.data["currentPassword"]):
            user.set_password(serializer.data["newPassword"])
            user.save()

            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=["post"])
    def avatar(self, request):
        """Метод для смены аватарки"""
        user_profile = Profile.objects.get(user=request.user)
        self.check_object_permissions(request, user_profile)
        current_avatar_path = os.path.join(
            settings.MEDIA_ROOT, str(user_profile.avatar)
        )
        serializer = self.get_serializer(data=request.data, instance=user_profile)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if os.path.isfile(current_avatar_path):
            os.remove(current_avatar_path)

        return Response(status=status.HTTP_200_OK)


class ProfileAPIView(APIView):
    """APIView для работы с моделью `Profile`"""

    serializer_class = ProfileSerializer
    permission_classes = (IsCurrentUserProfileOrAdmin,)

    @extend_schema(
        tags=["profile"],
        summary="Посмотреть собственный профиль",
        description="Get user profile",
    )
    def get(self, request):
        """Получаем информацию о текущем пользователе из его профиля без `id`"""
        user_profile = get_object_or_404(Profile, user=request.user)
        self.check_object_permissions(request, user_profile)
        serializer = self.serializer_class(user_profile)

        return Response(serializer.data, status=status.HTTP_200_OK)
