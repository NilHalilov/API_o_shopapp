"""Модуль для описания модели 'Profile' для БД"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models


User = get_user_model()


def user_avatar_directory_path(instance: "Profile", filename: str) -> str:
    return f"profiles/user_{instance.user.pk}/avatar/{filename}"


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )
    middle_name = models.CharField(max_length=100, verbose_name="Отчество")
    email = models.EmailField(
        max_length=60, unique=True, verbose_name="Электронная почта"
    )
    phone = models.CharField(
        validators=[
            RegexValidator(
                regex=r"^\d{11}$",
                message="Номер должен состоять из 11 цифр.",
            ),
        ],
        max_length=11,
        unique=True,
        verbose_name="Номер телефона",
    )
    avatar = models.ImageField(
        upload_to=user_avatar_directory_path,
        blank=True,
        null=True,
        verbose_name="Аватарка",
    )

    class Meta:
        db_table = "profile"
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"Профиль пользователя: {self.user.last_name} {self.user.first_name} {self.middle_name}"

    def show_full_name_with_patronymic(self):
        return f"{self.user.last_name} {self.user.first_name} {self.middle_name}"

    def show_avatar_info(self):
        return {
            "src": f"{settings.MEDIA_URL}{self.avatar}",
            "alt": f"Avatar of {self.user.last_name} {self.user.first_name}",
        }
