"""Модуль для описания представлений для модели 'Basket'"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet

from baskets.models import Basket
from baskets.serializers import DeleteFromBasketSerializer, ShowBasketItemSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["basket"],
        summary="Получить список товаров в корзине",
        description="Get all user products in basket",
    ),
    create=extend_schema(
        tags=["basket"],
        summary="Добавить товар в корзину",
        description="Add product in basket",
    ),
    destroy=extend_schema(
        tags=["basket"],
        summary="Удалить полностью товар из корзины или учитывая количество",
        description="Delete product from basket",
        # request=ShowBasketItemSerializer,
        # methods=['DELETE'],
    ),
)
class BasketViewSet(
    ListModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet
):
    """ViewSet для работы с моделью `Basket`"""

    serializer_class = ShowBasketItemSerializer

    def get_queryset(self):
        """Получаем корзину пользователя"""
        user = self.request.user

        if user.is_authenticated:
            return Basket.objects.filter(user=user).select_related("product")

        elif not self.request.session.session_key:
            self.request.session.create()

        return Basket.objects.filter(
            session_key=self.request.session.session_key
        ).select_related("product")

    def perform_create(self, serializer):
        """Метод для создания корзин"""
        serializer.save(session_key_for_anonym=self.request.session.session_key)

    def perform_destroy(self, instance):
        """Метод для удаления корзин"""
        deleted_count = self.request.data.get("count", None)
        count_in_basket = instance.count
        if deleted_count is not None and deleted_count < count_in_basket:
            instance.count -= deleted_count
            instance.save()
        else:
            instance.delete()
