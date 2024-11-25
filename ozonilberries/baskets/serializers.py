"""Модуль для описания сериалайзеров для модели 'Basket'"""

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from baskets.models import Basket
from products.models import Product
from products.serializers import ProductImageSerializer, ReviewSerializer, TagSerializer


class ShowBasketItemSerializer(serializers.ModelSerializer):
    """Класс сериалайзера для работы с моделью `Basket`"""

    id = serializers.IntegerField(source="product.id")
    category = serializers.IntegerField(source="product.category.id", read_only=True)
    price = serializers.DecimalField(
        source="products_price", max_digits=7, decimal_places=2, read_only=True
    )
    date = serializers.DateTimeField(source="created_at", read_only=True)
    title = serializers.CharField(source="product.title", read_only=True)
    description = serializers.CharField(source="product.description", read_only=True)
    freeDelivery = serializers.BooleanField(
        source="product.freeDelivery", read_only=True
    )
    images = serializers.SerializerMethodField()
    tags = TagSerializer(source="product.tags", many=True, read_only=True)
    reviews = serializers.IntegerField(source="product.reviews.count", read_only=True)
    rating = serializers.FloatField(source="product.show_rating", read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Basket
        fields = (
            "id",  # id товара
            "category",
            "price",
            "count",  # количество данного товара в корзине
            "date",  # дата добавления товара в корзину
            "title",
            "description",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "rating",
            "user",
        )

    @extend_schema_field(
        {
            "type": "string",
            "example": {
                "src": "string",
                "alt": "string",
            },
        }
    )
    def get_images(self, obj):
        all_images = obj.product.images.all()
        return ProductImageSerializer([img for img in all_images], many=True).data

    def validate(self, attrs):
        user_product = get_object_or_404(Product, id=attrs["product"]["id"])
        remaining_quantity = user_product.count - attrs["count"]

        if remaining_quantity < 0:
            raise serializers.ValidationError("Такого количества товара нет на складе")

        attrs["product_object"] = user_product
        return attrs

    def create(self, validated_data):
        current_basket = None
        purchased_product = validated_data["product_object"]

        if validated_data["user"].is_authenticated:
            current_basket, _ = Basket.objects.get_or_create(
                user=validated_data["user"],
                product=purchased_product,
            )
        elif validated_data["session_key_for_anonym"]:
            current_basket, _ = Basket.objects.get_or_create(
                session_key=validated_data["session_key_for_anonym"],
                product=purchased_product,
            )

        current_basket.count += validated_data["count"]
        current_basket.save()

        return current_basket


class DeleteFromBasketSerializer(serializers.Serializer):
    """Класс сериалайзера для удаления корзины"""

    id = serializers.IntegerField(min_value=0)
    count = serializers.IntegerField(min_value=0)
