"""Модуль для описания представлений для модели 'Order' и связанных с ней"""

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from orders.models import Order
from orders.serializers import (
    ConfirmOrderSerializer,
    OrderSerializer,
    PaymentSerializer,
)
from users.permissions import IsCurrentUserProfileOrAdmin


@extend_schema_view(
    list=extend_schema(
        tags=["order"],
        summary="Получить список активных заказов",
        description="Get all active order",
    ),
    create=extend_schema(
        tags=["order"],
        summary="Создать заказ",
        description="Create order",
    ),
    retrieve=extend_schema(
        tags=["order"],
        summary="Получить конкретный заказ",
        description="Get order",
    ),
)
class OrderViewSet(
    ListModelMixin, CreateModelMixin, RetrieveModelMixin, GenericViewSet
):
    """ViewSet для работы с моделью `Order`"""

    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Получаем список актуальных заказов"""
        return Order.objects.filter(
            user=self.request.user, status__in=["confirm_required", "confirmed"]
        ).order_by("-created_at")


class OrderConfirmAPIView(APIView):
    """APIView для работы с моделью `Order`"""

    serializer_class = ConfirmOrderSerializer
    permission_classes = (IsAuthenticated, IsCurrentUserProfileOrAdmin)

    @extend_schema(
        tags=["order"],
        summary="Подтвердить оформление заказа",
        description="Confirm order",
        operation_id="confirm_order",
    )
    def post(self, request, order_id):
        """Метод для подтверждения заказа по id"""
        order_qs = Order.objects.filter(status="confirm_required")
        user_order = get_object_or_404(order_qs, id=order_id)
        self.check_object_permissions(request, user_order)

        serializer = self.serializer_class(
            user_order, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_201_CREATED)


class SimulatedPaymentAPIView(APIView):
    """APIView для работы с моделью `Payment`"""

    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated, IsCurrentUserProfileOrAdmin)

    @extend_schema(
        tags=["payment"],
        description="payment",
        parameters=[
            OpenApiParameter(
                name="order_id",
                description="order id",
                location=OpenApiParameter.PATH,
                required=True,
                type=int,
            ),
        ],
    )
    def post(self, request, order_id):
        """Метод для симуляции оплаты подтвержденного заказа"""
        order_qs = Order.objects.filter(status="confirmed")
        user_order = get_object_or_404(order_qs, id=order_id)
        self.check_object_permissions(request, user_order)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(order=user_order)

        if user_order.status == "paid":
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
