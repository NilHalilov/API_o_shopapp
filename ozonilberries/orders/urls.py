"""Модуль для описания urls для модели 'Order' и связанных с ней"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from orders.views import OrderConfirmAPIView, OrderViewSet, SimulatedPaymentAPIView

app_name = "orders"

routers_orders = DefaultRouter()
routers_orders.register("orders", OrderViewSet, basename="orders")

urlpatterns = [
    path("", include(routers_orders.urls)),
]

urlpatterns += [
    path("orders/<int:order_id>", OrderConfirmAPIView.as_view(), name="order_confirm"),
    path(
        "payment/<int:order_id>",
        SimulatedPaymentAPIView.as_view(),
        name="order_payment",
    ),
]
