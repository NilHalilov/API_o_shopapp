"""Модуль для регистрации в административной панели Django модели 'Basket'"""

from django.contrib import admin

from baskets.models import Basket


class BasketInline(admin.TabularInline):

    model = Basket
    list_display = [
        "product",
        "count",
        "created_at",
    ]
    list_filter = [
        "product",
        "created_at",
    ]
    readonly_fields = [
        "created_at",
    ]
    extra = 1


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "product",
        "count",
        "created_at",
    ]
    list_filter = [
        "user",
        "product",
        "created_at",
    ]
    readonly_fields = list_display + ["session_key"]
