# Generated by Django 4.1.7 on 2023-08-14 08:48

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0014_alter_productsset_accessory_similarproducts'),
    ]

    operations = [
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size_from', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Размер от')),
                ('size_to', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Размер до')),
            ],
            options={
                'verbose_name': 'Размер',
                'verbose_name_plural': 'Размеры',
                'unique_together': {('size_from', 'size_to')},
            },
        ),
    ]
