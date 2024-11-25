"""Модуль для описания модели 'Basket' для БД"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from products.models import Product

User = get_user_model()


class BasketQueryset(models.QuerySet):

    def total_price(self):
        return sum(basket.products_price() for basket in self)

    def total_count(self):
        if self:
            return sum(basket.count for basket in self)
        return 0


class Basket(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Пользователь",
    )
    product = models.ForeignKey(
        to=Product, on_delete=models.CASCADE, verbose_name="Товар"
    )
    count = models.PositiveSmallIntegerField(default=0, verbose_name="Количество")
    session_key = models.CharField(max_length=32, null=True, blank=True)
    created_at = models.timestamp = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата добавления"
    )

    class Meta:
        db_table = "basket"
        verbose_name = "Корзину"
        verbose_name_plural = "Корзины"

    objects = BasketQueryset().as_manager()

    def products_price(self):
        try:
            return self.product.discounted.sale_price() * self.count
        except ObjectDoesNotExist:
            return self.product.price * self.count

    def __str__(self):
        if self.user:
            return f"Корзина: {self.user.username} * Товар: {self.product.title} * Количество: {self.count}"
        return f"Корзина: Анонимный пользователь * Товар: {self.product.title} * Количество: {self.count}"
