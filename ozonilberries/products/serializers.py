"""Модуль для описания сериалайзеров для модели 'Product' и связанных с ней"""

from django.conf import settings
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from products.models import (
    Category,
    Product,
    ProductImage,
    Review,
    Specification,
    Subcategory,
    Tag,
)


class ProductImageSerializer(serializers.ModelSerializer):
    """Класс сериалайзера для работы с изображениями модели `Product`"""

    # src = serializers.CharField(source='image')
    src = serializers.SerializerMethodField()
    alt = serializers.CharField(source="product.title")

    class Meta:
        model = ProductImage
        fields = (
            "src",
            "alt",
        )
        # extra_kwargs = {
        #     'src': {'source': 'image', 'read_only': True},
        #     'alt': {'source': 'product.title', 'read_only': True},
        # }

    def get_src(self, obj):
        full_path = f"{settings.MEDIA_URL}{obj.image}"
        return full_path


class SubcategorySerializer(serializers.ModelSerializer):
    """Класс сериалайзера для работы с подкатегориями модели `Product`"""

    image = serializers.DictField(
        source="show_image_info", child=serializers.CharField(), read_only=True
    )

    class Meta:
        model = Subcategory
        fields = (
            "id",
            "title",
            "image",
        )


class CategorySerializer(serializers.ModelSerializer):
    """Класс сериалайзера для работы с категориями модели `Product`"""

    image = serializers.DictField(
        source="show_image_info", child=serializers.CharField(), read_only=True
    )
    subcategories = SubcategorySerializer(many=True)

    class Meta:
        model = Category
        fields = (
            "id",
            "title",
            "image",
            "subcategories",
        )


class TagSerializer(serializers.ModelSerializer):
    """Класс сериалайзера для работы с тегами модели `Product`"""

    class Meta:
        model = Tag
        fields = "__all__"


class SpecificationSerializer(serializers.ModelSerializer):
    """Класс сериалайзера для работы со спецификациями модели `Product`"""

    class Meta:
        model = Specification
        fields = (
            "name",
            "value",
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Класс сериалайзера для работы с обзорами модели `Product`"""

    author = serializers.PrimaryKeyRelatedField(
        source="author.get_full_name", read_only=True
    )
    email = serializers.EmailField(source="author.profile.email", read_only=True)

    class Meta:
        model = Review
        fields = (
            "author",
            "email",
            "text",
            "rate",
            "date",
        )


class FullProductSerializer(serializers.ModelSerializer):
    """Класс сериалайзера для полного описания модели `Product`"""

    images = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    reviews = ReviewSerializer(many=True)
    specifications = SpecificationSerializer(many=True)
    rating = serializers.FloatField(source="show_rating")

    class Meta:
        model = Product
        fields = (
            "id",
            "category",
            "price",
            "count",  # количество данного товара в БД
            "date",  # дата добавления товара в БД
            "title",
            "description",
            "fullDescription",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "specifications",
            "rating",
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
        all_images = obj.images.all()
        return ProductImageSerializer([img for img in all_images], many=True).data


class PartialProductSerializer(serializers.ModelSerializer):
    """Класс сериалайзера для частичного описания модели `Product`"""

    images = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    reviews = serializers.IntegerField(source="show_reviews_count")
    rating = serializers.FloatField(source="show_rating")

    class Meta:
        model = Product
        fields = (
            "id",
            "category",
            "price",
            "count",
            "date",
            "title",
            "description",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "rating",
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
        all_images = obj.images.all()
        return ProductImageSerializer([img for img in all_images], many=True).data


class SalesProductSerializer(serializers.ModelSerializer):
    """Класс сериалайзера для работы со скидками модели `Product`"""

    images = serializers.SerializerMethodField()
    salePrice = serializers.DecimalField(
        source="discounted.sale_price", max_digits=7, decimal_places=2, read_only=True
    )
    dateFrom = serializers.DateField(source="discounted.dateFrom", read_only=True)
    dateTo = serializers.DateField(source="discounted.dateTo", read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "price",
            "salePrice",
            "dateFrom",
            "dateTo",
            "title",
            "images",
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
        all_images = obj.images.all()
        return ProductImageSerializer([img for img in all_images], many=True).data
