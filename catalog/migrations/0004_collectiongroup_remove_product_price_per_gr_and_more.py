# Generated by Django 4.1.7 on 2023-07-11 07:45

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_alter_productcost_size'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, verbose_name='Наименование')),
            ],
        ),
        migrations.RemoveField(
            model_name='product',
            name='price_per_gr',
        ),
        migrations.RemoveField(
            model_name='product',
            name='size',
        ),
        migrations.RemoveField(
            model_name='product',
            name='stock',
        ),
        migrations.RemoveField(
            model_name='product',
            name='weight',
        ),
        migrations.AddField(
            model_name='product',
            name='color',
            field=models.CharField(blank=True, db_index=True, max_length=50, verbose_name='Цвет'),
        ),
        migrations.AlterField(
            model_name='product',
            name='gender',
            field=models.CharField(choices=[('М', 'мужской'), ('Ж', 'женский'), ('Д', 'детский'), ('-', 'юнисекс')], db_index=True, default='-', max_length=10, verbose_name='Гендер'),
        ),
        migrations.CreateModel(
            name='StockAndCost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Вес')),
                ('size', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Размер')),
                ('stock', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Остаток')),
                ('cost', models.DecimalField(decimal_places=2, default=0, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Стоимость')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='catalog.product', verbose_name='Номенклатура')),
            ],
            options={
                'verbose_name': 'Наличие и стоимость изделия',
                'verbose_name_plural': 'Наличие и стоимость изделий',
            },
        ),
        migrations.AddField(
            model_name='collection',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='collections', to='catalog.collectiongroup', verbose_name='Группа'),
        ),
    ]
