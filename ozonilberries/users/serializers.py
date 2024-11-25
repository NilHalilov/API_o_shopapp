"""Модуль для описания сериалайзеров для модели 'Profile'"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from users.models import Profile

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    """Класс сериалайзера для работы с моделью `Profile`"""

    fullName = serializers.CharField(source="show_full_name_with_patronymic")
    middle_name = serializers.HiddenField(default="")
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    avatar = serializers.DictField(
        source="show_avatar_info", child=serializers.CharField(), read_only=True
    )

    class Meta:
        model = Profile
        fields = (
            "fullName",
            "email",
            "phone",
            "avatar",
            "middle_name",
            "user",
        )

    def validate_fullName(self, value):
        if len(value.split()) != 3:
            raise serializers.ValidationError(
                {"fullName": "Нужно ввести ФИО через пробел."}
            )

        return value

    def create(self, validated_data):
        current_user = validated_data.get("user")
        full_name_list = validated_data.pop("show_full_name_with_patronymic").split()

        current_user.first_name = full_name_list[1]
        current_user.last_name = full_name_list[0]
        current_user.save()

        validated_data["middle_name"] = full_name_list[2]
        new_profile, _ = Profile.objects.update_or_create(
            user=current_user,
            defaults=validated_data,
        )

        return new_profile


class ProfilePasswordSerializer(serializers.Serializer):
    """Класс сериалайзера для работы с паролем профиля"""

    currentPassword = serializers.CharField(max_length=150)
    newPassword = serializers.CharField(max_length=150)

    def validate_newPassword(self, value):
        validate_password(value)

        return value


class ProfileAvatarSerializer(serializers.ModelSerializer):
    """Класс сериалайзера для работы с аватаром профиля"""

    avatar = serializers.ImageField()

    class Meta:
        model = Profile
        fields = ("avatar",)

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get("avatar", instance.avatar)
        instance.save()

        return instance
