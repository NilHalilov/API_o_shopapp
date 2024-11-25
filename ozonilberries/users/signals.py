"""Модуль для описания сигналов для модели 'Profile'"""

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from orders.models import Order
from users.models import Profile


User = get_user_model()


@receiver(post_save, sender=Order)
def post_save_order(sender, instance: Order, created, **kwargs):
    """Сигнал для создания нового профиля, после успешного подтверждения заказа"""
    if not created:
        if hasattr(instance, "order_fullName"):
            current_user = User.objects.get(id=instance.user.id)
            full_name_list = instance.order_fullName.split()

            current_user.first_name = full_name_list[1]
            current_user.last_name = full_name_list[0]
            current_user.save()

            new_profile_data = {
                "middle_name": full_name_list[2],
                "email": instance.order_email,
                "phone": instance.order_phone,
            }
            new_profile, _ = Profile.objects.update_or_create(
                user=instance.user,
                defaults=new_profile_data,
            )
