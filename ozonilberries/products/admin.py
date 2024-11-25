"""Модуль для регистрации в административной панели Django модели 'Product' и связанных с ней"""

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from products.models import (
    Category,
    Product,
    ProductImage,
    Review,
    Sale,
    Specification,
    Subcategory,
    Tag,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


@admin.action(description='Пометить товар как "Доступный"')
def mark_available(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet
):
    queryset.update(is_available=True)


@admin.action(description='Пометить товар как "Лимитированный"')
def mark_limited(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet
):
    queryset.update(is_limited=True)


class ProductImageTabularAdmin(admin.TabularInline):
    model = ProductImage
    fields = [
        "image",
    ]
    extra = 0


class SpecificationTabularAdmin(admin.TabularInline):
    model = Specification
    fields = [
        "name",
        "value",
    ]
    extra = 0


class SaleTabularAdmin(admin.TabularInline):
    model = Sale
    fields = [
        "discount",
        "dateFrom",
        "dateTo",
    ]
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    ordering = "title", "price"
    actions = [
        mark_available,
        mark_limited,
    ]

    list_display = [
        "title",
        "get_full_description_short",
        "count",
        "price",
        "get_discount",
        "is_available",
    ]
    list_editable = [
        "is_available",
    ]
    search_fields = [
        "title",
        "description",
        "fullDescription",
    ]
    list_filter = [
        "price",
        "category",
        "subcategory",
        "tags",
    ]
    fields = [
        ("title", "slug"),
        "description",
        "fullDescription",
        ("price", "count"),
        ("category", "subcategory"),
        "tags",
        (
            "is_available",
            "is_limited",
            "freeDelivery",
        ),
    ]
    inlines = SaleTabularAdmin, ProductImageTabularAdmin, SpecificationTabularAdmin

    @admin.display(description="DISCOUNT", ordering="discounted__discount")
    def get_discount(self, obj):
        return obj.discounted.discount

    @admin.display(description="Полное описание", ordering="discounted__discount")
    def get_full_description_short(self, obj):
        if len(obj.fullDescription) < 40:
            return obj.fullDescription
        return obj.fullDescription[:48] + "..."

    def get_queryset(self, request):
        return Product.objects.select_related("discounted")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        "author",
        "product",
        "rate",
    ]

    list_filter = [
        "author",
        "product",
        "rate",
    ]
    list_display_links = [
        "product",
    ]
    readonly_fields = [
        "author",
        "product",
        "text",
        "rate",
    ]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "discount",
        "dateFrom",
        "dateTo",
    ]
    list_editable = [
        "discount",
        "dateTo",
    ]
