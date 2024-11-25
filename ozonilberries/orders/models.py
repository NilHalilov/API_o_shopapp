"""Модуль для описания модели 'Order' для БД и связанных с ней"""

from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import RegexValidator
from django.db import models

from products.models import Product

User = get_user_model()


class Order(models.Model):

    class DeliveryChoice(models.TextChoices):
        delivery = "delivery", "Обычная доставка"
        express = "express", "экспресс-доставка"

    class PaymentChoice(models.TextChoices):
        online_card = "online_card", "Картой онлайн"
        online_account = "online_account", "Со счёта онлайн"

    class OrderStatusChoice(models.TextChoices):
        confirm_required = "confirm_required", "Требуется подтверждение"
        confirmed = "confirmed", "Подтверждён"
        paid = "paid", "Оплачен"
        sent = "sent", "Отправлен"
        delivered = "delivered", "Доставлен"
        cancel = "cancel", "Отменён"

    user = models.ForeignKey(
        to=User,
        on_delete=models.SET_DEFAULT,
        default=None,
        blank=True,
        null=True,
        verbose_name="Пользователь",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания заказа"
    )
    city = models.CharField(max_length=80, default="", verbose_name="Город доставки")
    delivery_address = models.CharField(
        max_length=200, default="", verbose_name="Адрес доставки"
    )
    delivery_type = models.CharField(
        max_length=30,
        choices=DeliveryChoice.choices,
        default=DeliveryChoice.delivery,
        verbose_name="Тип доставки",
    )
    payment_type = models.CharField(
        max_length=30,
        choices=PaymentChoice.choices,
        default=PaymentChoice.online_card,
        verbose_name="Тип оплаты",
    )
    total_price = models.DecimalField(
        default=0.00, max_digits=10, decimal_places=2, verbose_name="Cумма заказа"
    )
    status = models.CharField(
        max_length=50,
        choices=OrderStatusChoice.choices,
        default=OrderStatusChoice.confirm_required,
        verbose_name="Статус заказа",
    )
    user_comment = models.TextField(
        blank=True, null=True, verbose_name="Комментарий к заказу"
    )

    class Meta:
        db_table = "order"
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        try:
            return f"Заказ №{self.pk} * (телефон: {self.user.profile.phone})"
        except ObjectDoesNotExist:
            return f"Заказ №{self.pk} * (телефон: Не указан)"


class OrderItem(models.Model):
    order = models.ForeignKey(
        to=Order,
        on_delete=models.CASCADE,
        related_name="product_items",
        verbose_name="Заказ",
    )
    product = models.ForeignKey(
        to=Product,
        on_delete=models.SET_DEFAULT,
        default=None,
        null=True,
        related_name="order_items",
        verbose_name="Продукт",
    )
    name = models.CharField(max_length=150, verbose_name="Название")
    price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Цена")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Количество")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата продажи")

    class Meta:
        db_table = "order_item"
        verbose_name = "Товар заказа"
        verbose_name_plural = "Проданные товары"

    def __str__(self):
        return f"Заказ №{self.order.id} * Товар {self.name}"

    def products_price(self):
        return round(self.price * self.quantity, 2)


class DeliveryCost(models.Model):
    delivery_price = models.DecimalField(
        default=0.00, max_digits=7, decimal_places=2, verbose_name="Цена доставки"
    )
    express_delivery_price = models.DecimalField(
        default=0.00,
        max_digits=7,
        decimal_places=2,
        verbose_name="Цена экспресс доставки",
    )
    free_delivery_border = models.DecimalField(
        default=0.00,
        max_digits=7,
        decimal_places=2,
        verbose_name="Порог для бесплатной доставки",
    )
    is_active = models.BooleanField(default=False)

    class Meta:
        db_table = "delivery_cost"
        verbose_name = "Стоимость доставки"
        verbose_name_plural = "Стоимости доставок"

    def __str__(self):
        return f"Доставка {self.delivery_price} * Экспресс {self.express_delivery_price} * Бесплатно от {self.free_delivery_border}"


def validate_expiry_period(user_year: str):
    try:
        validating_year = int(user_year)
    except ValueError:
        raise ValidationError(
            "Год истечения срока действия карты должен содержать только цифры."
        )

    if date.today().year > validating_year:
        raise ValidationError(
            "Год истечения срока действия карты должен быть не меньше текущего."
        )
    return user_year


class Payment(models.Model):
    order = models.OneToOneField(
        to=Order, on_delete=models.CASCADE, related_name="payment", verbose_name="Заказ"
    )
    name = models.CharField(max_length=150, verbose_name="Владелец карты")
    number = models.CharField(
        validators=[
            RegexValidator(
                regex=r"^\d{1,8}$",
                message="Номер  должен быть не длиннее 8 цифр.",
            ),
        ],
        max_length=8,
        verbose_name="Номер карты/счёта",
    )

    code = models.CharField(
        validators=[
            RegexValidator(
                regex=r"^\d{3}$",
                message="Код  должен состоять из 3 цифр.",
            ),
        ],
        max_length=3,
        verbose_name="Код",
    )

    month = models.CharField(
        validators=[
            RegexValidator(
                regex=r"^[0]?[1-9]{1}$|^[1]{1}[0-2]{1}$",
                message="Введите номер месяца с карты.",
            ),
        ],
        max_length=2,
        verbose_name="month_valid_thru",
    )

    year = models.CharField(
        validators=[
            RegexValidator(
                regex=r"^\d{4}$",
                message="Год должен состоять из 4 цифр.",
            ),
            validate_expiry_period,
        ],
        max_length=4,
        verbose_name="year_valid_thru",
    )

    payment_error_message = models.TextField(
        blank=True, null=True, verbose_name="Текст ошибки оплаты"
    )
    is_paid = models.BooleanField(default=False, verbose_name="Оплачено")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")

    class Meta:
        db_table = "order_payment"
        verbose_name = "Оплата заказа"
        verbose_name_plural = "Оплаты заказов"

    def __str__(self):
        return f"{self.order}, оплачено: {self.is_paid}"
