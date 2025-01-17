# Generated by Django 4.2.14 on 2024-11-18 15:51

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="phone",
            field=models.CharField(
                max_length=11,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Номер должен состоять из 11 цифр.", regex="^\\d{11}$"
                    )
                ],
                verbose_name="Номер телефона",
            ),
        ),
    ]
