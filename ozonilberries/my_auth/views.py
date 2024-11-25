"""Модуль для описания представлений для аутентификации пользователя"""

import json

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.models import update_last_login
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from baskets.models import Basket
from my_auth.serializers import (
    UserLogInSerializer,
    UserLogOutSerializer,
    UserRegistrationSerializer,
)

User = get_user_model()


@extend_schema(
    tags=["auth"],
    summary="Регистрация пользователя",
    description="User sign up",
)
class UserRegistrationViewSet(CreateModelMixin, GenericViewSet):
    """ViewSet для работы регистрации пользователя"""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        """Метод для регистрации нового пользователя"""
        data = None
        if "username" in request.data and "password" in request.data:
            data = request.data

        else:
            for _key in request.data:
                if "username" in _key and "password" in _key:
                    data = json.loads(_key)
                    break

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        new_user = serializer.save()

        session_key = (
            request.session.session_key
        )  # для корзины незарегистрированного пользователя

        login(request, new_user)

        if session_key:
            Basket.objects.filter(session_key=session_key).update(
                user=new_user, session_key=None
            )  # для корзины незарегистрированного пользователя

        headers = self.get_success_headers(request.data)
        return Response(status=status.HTTP_201_CREATED, headers=headers)


class UserLogInAPIView(APIView):
    """APIView для входа пользователя в систему"""

    serializer_class = UserLogInSerializer

    @extend_schema(
        tags=["auth"],
        summary="Авторизация пользователя",
        description="User log in",
        request=UserLogInSerializer,
    )
    def post(self, request):
        """Метод для входа пользователя в систему"""
        data = None
        if "username" in request.data and "password" in request.data:
            data = request.data
        else:
            for _key in request.data:
                if "username" in _key and "password" in _key:
                    data = json.loads(_key)
                    break

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=serializer.data["username"],
            password=serializer.data["password"],
        )

        if user is None:
            return Response(
                {
                    "error_message": "Такой пользователь не найден, либо аккаунт не активен",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        session_key = (
            request.session.session_key
        )  # для корзины незарегистрированного пользователя

        update_last_login(None, user)
        login(request, user)

        if session_key:
            Basket.objects.filter(session_key=session_key).update(
                user=user, session_key=None
            )  # для корзины незарегистрированного пользователя

        return Response(status=status.HTTP_200_OK)


class UserLogOutAPIView(APIView):
    """APIView для выхода пользователя из системы"""

    serializer_class = UserLogOutSerializer
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["auth"],
        summary="Выход пользователя из системы",
        description="User log out",
    )
    def post(self, request):
        """Метод для выхода пользователя из системы"""
        logout(request)

        return Response(status=status.HTTP_200_OK)
