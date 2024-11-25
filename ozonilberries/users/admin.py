"""Модуль для регистрации в административной панели Django модели 'Profile'"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from baskets.admin import BasketInline
from orders.admin import OrderTabularAdmin
from users.models import Profile


class UserAdmin(BaseUserAdmin):

    inlines = [BasketInline, OrderTabularAdmin]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "get_username",
        "get_first_name",
        "get_last_name",
        "email",
        "phone",
    ]
    search_fields = [
        "email",
        "phone",
    ]

    @admin.display(description="Имя", ordering="user__first_name")
    def get_first_name(self, obj):
        return obj.user.first_name

    @admin.display(description="Фамилия", ordering="user__last_name")
    def get_last_name(self, obj):
        return obj.user.last_name

    @admin.display(description="Никнэйм", ordering="user__username")
    def get_username(self, obj):
        return obj.user.username

    def get_queryset(self, request):
        return Profile.objects.select_related("user")


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
