# Generated by Django 4.2.14 on 2024-11-07 11:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryCost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=7, verbose_name='Цена доставки')),
                ('express_delivery_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=7, verbose_name='Цена экспресс доставки')),
                ('free_delivery_border', models.DecimalField(decimal_places=2, default=0.0, max_digits=7, verbose_name='Порог для бесплатной доставки')),
                ('is_active', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Стоимость доставки',
                'verbose_name_plural': 'Стоимости доставок',
                'db_table': 'delivery_cost',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания заказа')),
                ('city', models.CharField(default='', max_length=80, verbose_name='Город доставки')),
                ('delivery_address', models.CharField(default='', max_length=200, verbose_name='Адрес доставки')),
                ('delivery_type', models.CharField(choices=[('delivery', 'Обычная доставка'), ('express', 'экспресс-доставка')], default='delivery', max_length=30, verbose_name='Тип доставки')),
                ('payment_type', models.CharField(choices=[('online_card', 'Картой онлайн'), ('online_account', 'Со счёта онлайн')], default='online_card', max_length=30, verbose_name='Тип оплаты')),
                ('total_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Cумма заказа')),
                ('status', models.CharField(choices=[('in_process', 'В процессе'), ('sent', 'Отправлен'), ('delivered', 'Доставлен'), ('cancel', 'Отменён')], default='in_process', max_length=50, verbose_name='Статус заказа')),
                ('user_comment', models.TextField(blank=True, null=True, verbose_name='Комментарий к заказу')),
                ('user', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказы',
                'db_table': 'order',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Название')),
                ('price', models.DecimalField(decimal_places=2, max_digits=7, verbose_name='Цена')),
                ('quantity', models.PositiveIntegerField(default=0, verbose_name='Количество')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата продажи')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_items', to='orders.order', verbose_name='Заказ')),
                ('product', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='order_items', to='products.product', verbose_name='Продукт')),
            ],
            options={
                'verbose_name': 'Проданный товар',
                'verbose_name_plural': 'Проданные товары',
                'db_table': 'order_item',
            },
        ),
    ]
