# Generated by Django 4.1.7 on 2023-08-30 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0021_auto_20230824_1333'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gender',
            options={'verbose_name': 'Гендер', 'verbose_name_plural': 'Гендер'},
        ),
        migrations.AddField(
            model_name='product',
            name='metal_finish',
            field=models.CharField(blank=True, db_index=True, max_length=50, verbose_name='Обработка металла'),
        ),
    ]
