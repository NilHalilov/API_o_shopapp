"""Модуль для описания сериалайзеров для аутентификации пользователя"""

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Класс сериалайзера для регистрации пользователя"""

    name = serializers.CharField(source="first_name")
    # password_confirm = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = (
            "name",
            "username",
            "password",
            # 'password_confirm',
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, attrs):
        # if attrs['password'] != attrs['password_confirm']:
        #     raise serializers.ValidationError({'password': 'Введённые пароли не совпадают.'})

        validate_password(attrs["password"])

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            password=make_password(validated_data["password"]),
        )

        return user


class UserLogInSerializer(serializers.Serializer):
    """Класс сериалайзера для входа пользователя в систему"""

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=150)


class UserLogOutSerializer(serializers.Serializer):
    """Класс сериалайзера для выхода пользователя из системы"""
    pass
