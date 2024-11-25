"""Модуль для регистрации в административной панели Django модели 'Order' и связанных с ней"""

from django.contrib import admin

from orders.models import DeliveryCost, Order, OrderItem, Payment


class OrderTabularAdmin(admin.TabularInline):
    model = Order
    fields = [
        "delivery_type",
        "payment_type",
        "status",
        "created_at",
    ]
    search_fields = [
        "status",
        "created_at",
    ]
    readonly_fields = ("created_at",)
    extra = 0


class PaymentTabularAdmin(admin.TabularInline):
    model = Payment
    fields = [
        "payment_error_message",
        "is_paid",
        "created_at",
    ]
    readonly_fields = fields
    extra = 0


class OrderItemTabularAdmin(admin.TabularInline):
    model = OrderItem
    fields = [
        "product",
        "name",
        "price",
        "quantity",
    ]
    search_fields = [
        "product",
        "name",
    ]
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        return Order.objects.select_related("user")

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username

    list_display = [
        "user_verbose",
        "delivery_address",
        "delivery_type",
        "payment_type",
        "total_price",
        "status",
        "created_at",
    ]
    search_fields = [
        "id",
    ]
    readonly_fields = ("created_at",)
    list_filter = [
        "delivery_type",
        "payment_type",
        "total_price",
        "status",
    ]
    inlines = OrderItemTabularAdmin, PaymentTabularAdmin


@admin.register(DeliveryCost)
class DeliveryCostAdmin(admin.ModelAdmin):
    list_display = [
        "delivery_price",
        "express_delivery_price",
        "free_delivery_border",
        "is_active",
    ]
    list_display_links = [
        "delivery_price",
        "express_delivery_price",
        "free_delivery_border",
    ]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        "order",
        "product",
        "name",
        "price",
        "quantity",
    ]
    search_fields = [
        "order",
        "product",
        "name",
    ]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "order",
        "name",
        "number",
        "month",
        "year",
        "is_paid",
        "created_at",
    ]
    search_fields = [
        "number",
        "order",
    ]
    readonly_fields = [
        "order",
        "name",
        "number",
        "month",
        "year",
        "is_paid",
        "payment_error_message",
        "code",
        "created_at",
    ]
    list_filter = [
        "is_paid",
    ]
