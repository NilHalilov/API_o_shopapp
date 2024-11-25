"""Модуль для описания модели 'Product' для БД и связанных с ней"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg

User = get_user_model()


class GetImageInfoMixin:

    def show_image_info(self):
        return {
            "src": f"{settings.MEDIA_URL}{self.image}",
            "alt": self.title,
        }


def product_category_directory_path(instance: "Category", filename: str) -> str:
    return f"categories/category_{instance.id}/{filename}"


def product_subcategory_directory_path(instance: "Subcategory", filename: str) -> str:
    return f"subcategories/subcategory_{instance.id}/{filename}"


def product_images_directory_path(instance: "ProductImage", filename: str) -> str:
    return f"goods/product_{instance.product.id}/{filename}"


class Subcategory(GetImageInfoMixin, models.Model):
    title = models.CharField(max_length=150, unique=True, verbose_name="Название")
    slug = models.SlugField(
        max_length=200, unique=True, blank=True, null=True, verbose_name="URL"
    )
    image = models.ImageField(
        upload_to=product_subcategory_directory_path,
        blank=True,
        null=True,
        verbose_name="Изображение",
    )

    class Meta:
        db_table = "subcategory"
        verbose_name = "Подкатегорию"
        verbose_name_plural = "Подкатегории"

    def __str__(self):
        return self.title


class Category(GetImageInfoMixin, models.Model):
    title = models.CharField(max_length=150, unique=True, verbose_name="Название")
    slug = models.SlugField(
        max_length=200, unique=True, blank=True, null=True, verbose_name="URL"
    )
    image = models.ImageField(
        upload_to=product_category_directory_path,
        blank=True,
        null=True,
        verbose_name="Изображение",
    )
    subcategories = models.ManyToManyField(
        to=Subcategory, related_name="categories", verbose_name="Подкатегория"
    )

    class Meta:
        db_table = "category"
        verbose_name = "Категорию"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Название")

    class Meta:
        db_table = "tag"
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=150, unique=True, verbose_name="Название")
    description = models.CharField(
        max_length=400, blank=True, null=True, verbose_name="Краткое описание"
    )
    fullDescription = models.TextField(
        blank=True, null=True, verbose_name="Полное описание"
    )
    category = models.ForeignKey(
        to=Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Категория",
    )
    subcategory = models.ForeignKey(
        to=Subcategory,
        on_delete=models.CASCADE,
        related_name="subcategories",
        verbose_name="Подкатегория",
    )
    price = models.DecimalField(
        default=0.00, max_digits=7, decimal_places=2, verbose_name="Цена"
    )
    tags = models.ManyToManyField(
        to=Tag, related_name="products", verbose_name="Тэги продукта"
    )
    slug = models.SlugField(
        max_length=200, unique=True, blank=True, null=True, verbose_name="URL"
    )
    count = models.PositiveIntegerField(default=0, verbose_name="Количество")
    # sold_count = models.PositiveIntegerField(default=0, verbose_name='Количество проданного')
    freeDelivery = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)
    is_limited = models.BooleanField(default=False)

    class Meta:
        db_table = "product"
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return f"{self.title!r}: кол-во {self.count}"

    def display_id(self):
        return f"{self.id:05}"

    def show_rating(self):
        rating = self.reviews.aggregate(Avg("rate"))
        if not rating["rate__avg"]:
            return 0.0
        return round(rating["rate__avg"], 1)

    def show_reviews_count(self):
        return self.reviews.count()


class Sale(models.Model):
    product = models.OneToOneField(
        to=Product,
        on_delete=models.CASCADE,
        related_name="discounted",
        verbose_name="Товар",
    )
    discount = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Скидка в %"
    )
    dateFrom = models.DateField(verbose_name="Начало распродажи",)
    dateTo = models.DateField(verbose_name="Конец распродажи",)

    class Meta:
        db_table = "sale"
        verbose_name = "Скидка"
        verbose_name_plural = "Скидки"

    def sale_price(self):
        if self.discount != 0:
            return round(
                self.product.price - (self.product.price * self.discount) / 100, 2
            )
        return self.product.price

    def __str__(self):
        return f"Текущая скидка на товар: {self.product.title} _{self.discount}% до {self.dateTo} числа."


class ProductImage(models.Model):
    image = models.ImageField(
        upload_to=product_images_directory_path,
        blank=True,
        null=True,
        verbose_name="Изображение",
    )
    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Изображенный товар",
    )

    class Meta:
        db_table = "product_image"
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"

    def __str__(self):
        return f"Изображение товара: {self.product.title}"


class Review(models.Model):
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Автор обзора",
    )
    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Обозреваемый товар",
    )
    text = models.TextField(blank=True, null=True, verbose_name="Обзор")
    rate = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name="Оценка",
    )
    date = models.DateTimeField(auto_now_add=True, verbose_name="Время создания обзора")

    class Meta:
        db_table = "review"
        verbose_name = "Обзор"
        verbose_name_plural = "Обзоры"
        constraints = [
            models.CheckConstraint(
                check=models.Q(rate__gte=0) & models.Q(rate__lte=5),
                name="Оценка должна быть от 0 до 5",
            )
        ]

    def __str__(self):
        return f"Оценка на {self.product.title} от {self.author}"


class Specification(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Название")
    value = models.TextField(blank=True, null=True, verbose_name="Параметры")
    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
        related_name="specifications",
        verbose_name="Товар",
    )

    class Meta:
        db_table = "specification"
        verbose_name = "Спецификация"
        verbose_name_plural = "Спецификации"

    def __str__(self):
        return self.name
