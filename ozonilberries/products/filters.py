"""Модуль для описания кастомных фильтров связанных с моделью `Product`"""

import django_filters

from products.models import Product, Tag


class ProductFilter(django_filters.FilterSet):
    """Фильтр продуктов для каталога"""

    name = django_filters.CharFilter(
        field_name="title", lookup_expr="icontains", label="Наименование товара"
    )
    minPrice = django_filters.NumberFilter(
        field_name="price", lookup_expr="gte", label="Минимальная цена"
    )
    maxPrice = django_filters.NumberFilter(
        field_name="price", lookup_expr="lte", label="Максимальная цена"
    )
    freeDelivery = django_filters.BooleanFilter(
        field_name="freeDelivery", label="Бесплатная доставка"
    )
    available = django_filters.BooleanFilter(
        field_name="is_available", label="В наличии"
    )

    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(), field_name="tags", label="Тэги"
    )

    order_by = django_filters.OrderingFilter(
        fields=(
            ("price", "price"),
            ("reviews", "reviews"),
            ("rating", "rating"),
            ("date", "date"),
        )
    )

    class Meta:
        model = Product
        fields = []
