# Generated by Django 4.1.7 on 2023-05-15 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_pricetype_client'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='unit',
            field=models.CharField(choices=[('796', 'штук'), ('163', 'грамм')], db_index=True, default='грамм', max_length=20, verbose_name='Единица измерения'),
        ),
    ]
