# Generated by Django 4.1.7 on 2023-07-11 08:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_alter_price_product_alter_price_type_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProductCost',
        ),
    ]
