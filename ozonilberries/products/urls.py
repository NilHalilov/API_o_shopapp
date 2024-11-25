"""Модуль для описания urls для модели 'Product' и связанных с ней"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from products.views import (
    BannerProductsViewSet,
    CatalogViewSet,
    CategoryViewSet,
    OneProductViewSet,
    ProductsViewSet,
    SalesProductsViewSet,
    TagViewSet,
)

app_name = "products"

routers_products = DefaultRouter()
routers_products.register("categories", CategoryViewSet, basename="categories")
routers_products.register("tags", TagViewSet, basename="tags")
routers_products.register("product", OneProductViewSet, basename="product")
routers_products.register("catalog", CatalogViewSet, basename="catalog")
routers_products.register("products", ProductsViewSet, basename="products")
routers_products.register("sales", SalesProductsViewSet, basename="sales")
routers_products.register("banners", BannerProductsViewSet, basename="banners")

urlpatterns = [
    path("", include(routers_products.urls)),
]
