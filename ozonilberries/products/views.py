"""Модуль для описания представлений для модели 'Product' и связанных с ней"""

from datetime import date

from django.db.models import Avg, F
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from products.filters import ProductFilter
from products.models import Category, Product, Review, Sale, Tag
from products.serializers import (
    CategorySerializer,
    FullProductSerializer,
    PartialProductSerializer,
    ReviewSerializer,
    SalesProductSerializer,
    TagSerializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=["catalog"],
        summary="Получить список категорий",
        description="Get all categories",
    )
)
class CategoryViewSet(ListModelMixin, GenericViewSet):
    """ViewSet для работы с моделью `Category`"""

    queryset = Category.objects.prefetch_related("subcategories")
    serializer_class = CategorySerializer


@extend_schema_view(
    list=extend_schema(
        tags=["catalog"],
        summary="Получить список товаров каталога",
        description="Get all products or get products from one requested category",
        parameters=[
            OpenApiParameter(
                name="category_id",
                description="category id",
                location=OpenApiParameter.QUERY,
                required=False,
                type=int,
            ),
        ],
    )
)
class CatalogViewSet(ListModelMixin, GenericViewSet):
    """ViewSet для работы с каталогом продуктов"""

    serializer_class = PartialProductSerializer
    filterset_class = ProductFilter

    def get_queryset(self):
        """Получаем каталог продуктов для указанной категории или весь каталог"""
        category_id = self.request.query_params.get("category_id", None)
        if category_id:
            interested_category = get_object_or_404(Category, id=category_id)

            return (
                Product.objects.prefetch_related("images")
                .prefetch_related("tags")
                .prefetch_related("reviews")
                .filter(category=interested_category)
            )

        return (
            Product.objects.prefetch_related("images")
            .prefetch_related("tags")
            .prefetch_related("reviews")
        )


@extend_schema_view(
    list=extend_schema(
        tags=["tags"],
        summary="Получить список тэгов",
        description="Get all tags or get tags from one requested category",
        parameters=[
            OpenApiParameter(
                name="category_id",
                description="category id",
                location=OpenApiParameter.QUERY,
                required=False,
                type=int,
            ),
        ],
    )
)
class TagViewSet(ListModelMixin, GenericViewSet):
    """ViewSet для работы с моделью `Tag`"""

    serializer_class = TagSerializer

    def get_queryset(self):
        """Получаем теги для указанной категории или все теги"""
        category_id = self.request.query_params.get("category_id", None)
        if category_id:
            interested_category = get_object_or_404(Category, id=category_id)

            return Tag.objects.filter(
                products__category=interested_category.id
            ).distinct()

        return Tag.objects.all()


@extend_schema_view(
    retrieve=extend_schema(
        tags=["product"],
        summary="Посмотреть информацию о товаре",
        description="Get product by id",
        parameters=[
            OpenApiParameter(
                name="id",
                description="product id",
                location=OpenApiParameter.PATH,
                required=True,
                type=int,
            ),
        ],
    ),
    review=extend_schema(
        tags=["product"],
        summary="Оставить отзыв на продукт",
        description="Post product review",
        parameters=[
            OpenApiParameter(
                name="id",
                description="product id",
                location=OpenApiParameter.PATH,
                required=True,
                type=int,
            ),
        ],
    ),
)
class OneProductViewSet(RetrieveModelMixin, GenericViewSet):
    """ViewSet для работы с одним экземпляром модели `Product`"""

    def get_queryset(self):
        """Получаем указанный продукт"""
        if self.action in [
            "retrieve",
            "review",
        ]:
            return Product.objects.filter(id=self.kwargs.get("pk"))

        return Product.objects.all()

    def get_serializer_class(self):
        if self.action in [
            "review",
        ]:
            return ReviewSerializer

        return FullProductSerializer

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        """Метод для создания нового обзора на продукт"""
        user = request.user
        if user.is_authenticated:
            product_for_comment = self.get_object()
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(author=user, product=product_for_comment)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_401_UNAUTHORIZED)


@extend_schema_view(
    list=extend_schema(
        exclude=True,
    ),
    popular=extend_schema(
        tags=["catalog"],
        summary="Посмотреть популярные товары",
        description="Get catalog popular products",
    ),
    limited=extend_schema(
        tags=["catalog"],
        summary="Посмотреть ограниченный тираж",
        description="Get catalog limited products",
    ),
)
class ProductsViewSet(ListModelMixin, GenericViewSet):
    """ViewSet для работы с моделью `Product`"""

    serializer_class = PartialProductSerializer

    def get_queryset(self):
        if self.action == "popular":
            return (
                Product.objects.prefetch_related("images")
                .prefetch_related("tags")
                .prefetch_related("reviews")
                .annotate(rating=Avg("reviews__rate"))
                .order_by(F("rating").desc(nulls_last=True))[:8]
            )

        elif self.action == "limited":
            return (
                Product.objects.prefetch_related("images")
                .prefetch_related("tags")
                .prefetch_related("reviews")
                .filter(is_limited=True)[:16]
            )

        return Product.objects.all()

    @action(detail=False, methods=["get"])
    def popular(self, request, *args, **kwargs):
        """Метод для вывода списка самых популярных продуктов (8шт.)"""
        return self.list(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    def limited(self, request, *args, **kwargs):
        """Метод для вывода списка лимитированных продуктов (16шт.)"""
        return self.list(request, *args, **kwargs)


@extend_schema_view(
    list=extend_schema(
        tags=["catalog"],
        summary="Посмотреть товары со скидками",
        description="Get catalog sales products",
    ),
)
class SalesProductsViewSet(ListModelMixin, GenericViewSet):
    """ViewSet для работы с моделью `Sale`"""

    serializer_class = SalesProductSerializer

    def get_queryset(self):
        """Получаем товары с актуальными скидками"""
        actual_sales = Sale.objects.prefetch_related("images").filter(
            dateTo__gte=date.today()
        )
        return Product.objects.filter(discounted__in=actual_sales)


@extend_schema_view(
    list=extend_schema(
        tags=["catalog"],
        summary="Посмотреть случайные товары для банера",
        description="Get catalog banner products",
    ),
)
class BannerProductsViewSet(ListModelMixin, GenericViewSet):
    """ViewSet для работы с баннером продуктов`"""

    serializer_class = PartialProductSerializer

    def get_queryset(self):
        return (
            Product.objects.prefetch_related("images")
            .prefetch_related("tags")
            .prefetch_related("reviews")
            .annotate(rating=Avg("reviews__rate"))
            .extra(select={"random_id": "random()"})[:3]
        )
