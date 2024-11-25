"""Модуль для описания сериалайзеров для модели 'Order' и связанных с ней"""

from datetime import date

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.validators import RegexValidator
from django.db import transaction
from rest_framework import serializers

from baskets.models import Basket
from orders.models import DeliveryCost, Order, OrderItem, Payment
from products.models import Product
from products.serializers import PartialProductSerializer


class OrderSerializer(serializers.ModelSerializer):
    """Класс сериалайзера для модели `Order`"""

    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    fullName = serializers.CharField(
        source="user.profile.show_full_name_with_patronymic", read_only=True
    )
    email = serializers.EmailField(source="user.profile.email", read_only=True)
    phone = serializers.CharField(source="user.profile.phone", read_only=True)
    deliveryType = serializers.ChoiceField(
        source="delivery_type", choices=Order.DeliveryChoice, read_only=True
    )
    paymentType = serializers.ChoiceField(
        source="payment_type", choices=Order.PaymentChoice, read_only=True
    )
    totalCost = serializers.DecimalField(
        source="total_price", max_digits=10, decimal_places=2, read_only=True
    )
    address = serializers.CharField(source="delivery_address", read_only=True)
    products = serializers.SerializerMethodField()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Order
        fields = (
            "id",
            "createdAt",
            "fullName",
            "email",
            "phone",
            "deliveryType",
            "paymentType",
            "totalCost",
            "status",
            "city",
            "address",
            "products",
            "user",
        )
        read_only_fields = fields

    def get_products(self, obj):
        all_products_items = obj.product_items.all()
        return PartialProductSerializer(
            [_item.product for _item in all_products_items], many=True
        ).data

    def validate(self, attrs):
        user_basket = Basket.objects.filter(user=attrs["user"])
        if not user_basket:
            raise serializers.ValidationError("Ваша корзина пуста!")

        return attrs


class ConfirmOrderSerializer(serializers.HyperlinkedModelSerializer):
    """Класс сериалайзера для модели `Order` при подтверждении заказа"""

    fullName = serializers.CharField(
        source="user.profile.show_full_name_with_patronymic"
    )
    email = serializers.EmailField(source="user.profile.email")
    phone = serializers.CharField(
        source="user.profile.phone",
        validators=[
            RegexValidator(
                regex=r"^\d{11}$",
                message="Номер должен состоять из 11 цифр.",
            )
        ],
    )
    deliveryType = serializers.ChoiceField(
        source="delivery_type", choices=Order.DeliveryChoice
    )
    paymentType = serializers.ChoiceField(
        source="payment_type", choices=Order.PaymentChoice
    )
    totalCost = serializers.DecimalField(
        source="total_price", max_digits=10, decimal_places=2, read_only=True
    )
    address = serializers.CharField(source="delivery_address")
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Order
        fields = (
            "fullName",
            "email",
            "phone",
            "deliveryType",
            "paymentType",
            "totalCost",
            "status",
            "city",
            "address",
            "user",
        )

    def validate_fullName(self, value):
        if len(value.split()) != 3:
            raise serializers.ValidationError("Нужно ввести ФИО через пробел.")

    def validate(self, attrs):
        user_basket = Basket.objects.filter(user=attrs["user"])
        if not user_basket:
            raise serializers.ValidationError("Ваша корзина пуста!")
        try:
            delivery_conditions = DeliveryCost.objects.get(is_active=True)
            attrs["delivery_conditions"] = delivery_conditions
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            raise serializers.ValidationError(
                "Сообщение для администратора. Активно 0 или 1< условий для доставки. Требуется строго 1."
            )

        attrs["user_basket"] = user_basket
        return attrs

    def update(self, instance, validated_data):
        instance.order_fullName = self.context["request"].data["fullName"]
        instance.order_email = self.context["request"].data["email"]
        instance.order_phone = self.context["request"].data["phone"]

        with transaction.atomic():
            total_order_price = 0
            delivery_conditions = validated_data["delivery_conditions"]
            for _basket in validated_data["user_basket"]:
                product: Product = _basket.product
                name = _basket.product.title
                try:
                    price = _basket.product.discounted.sale_price()
                except ObjectDoesNotExist:
                    price = _basket.product.price
                quantity = _basket.count

                if product.count < quantity:
                    raise serializers.ValidationError(
                        f"Такого количества товара {name} нет на складе. В наличии - {product.count}"
                    )

                OrderItem.objects.create(
                    order=instance,
                    product=product,
                    name=name,
                    price=price,
                    quantity=quantity,
                )
                product.count -= quantity
                product.save()

                total_order_price += _basket.products_price()

            validated_data["user_basket"].delete()

            if total_order_price < delivery_conditions.free_delivery_border:
                total_order_price += delivery_conditions.delivery_price
            if validated_data["delivery_type"] == "express":
                total_order_price += delivery_conditions.express_delivery_price

            instance._fullName = self.context["request"].data["fullName"]
            instance._email = self.context["request"].data["email"]
            instance._phone = self.context["request"].data["phone"]

            instance.city = validated_data.get("city", instance.city)
            instance.delivery_address = validated_data.get(
                "delivery_address", instance.delivery_address
            )
            instance.delivery_type = validated_data.get(
                "delivery_type", instance.delivery_type
            )
            instance.payment_type = validated_data.get(
                "payment_type", instance.payment_type
            )
            instance.total_price = total_order_price
            # instance.status = validated_data.get('status', instance.status)
            instance.status = "confirmed"
            instance.user_comment = validated_data.get("user_comment", None)
            instance.save()

            return validated_data


class PaymentSerializer(serializers.ModelSerializer):
    """Класс сериалайзера для модели `Payment`"""

    class Meta:
        model = Payment
        fields = (
            "number",
            "name",
            "month",
            "year",
            "code",
        )

    def validate(self, attrs):
        _month = int(attrs["month"])
        _year = int(attrs["year"])
        if date(_year, _month, 1) < date.today():
            raise serializers.ValidationError("Истёк срока действия карты.")

        return attrs

    def create(self, validated_data):
        paid_order = validated_data["order"]
        error_message = None

        if int(validated_data["number"]) % 2 != 0:
            error_message = "Имитация ошибки чётности: `!=0`"
        elif validated_data["number"].endswith("0"):
            error_message = "Имитация ошибки номера карты: `endswith(0)`"

        payment_status = True if error_message is None else False

        with transaction.atomic():
            new_payment_data = {
                "name": validated_data["name"],
                "number": validated_data["number"],
                "code": validated_data["code"],
                "month": validated_data["month"],
                "year": validated_data["year"],
                "payment_error_message": error_message,
                "is_paid": payment_status,
            }

            new_payment, _ = Payment.objects.update_or_create(
                order=paid_order, defaults=new_payment_data
            )

            if payment_status:
                paid_order.status = "paid"
                paid_order.save()

            return validated_data
