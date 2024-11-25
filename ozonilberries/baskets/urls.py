"""Модуль для описания urls для модели 'Basket'"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from baskets.views import BasketViewSet

app_name = "baskets"

routers_baskets = DefaultRouter()
routers_baskets.register("basket", BasketViewSet, basename="basket")

urlpatterns = [
    path("", include(routers_baskets.urls)),
]
