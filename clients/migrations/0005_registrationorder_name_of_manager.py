# Generated by Django 4.1.7 on 2023-04-09 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0004_client_manager_alter_registrationorder_inn_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrationorder',
            name='name_of_manager',
            field=models.CharField(blank=True, max_length=150, verbose_name='ФИО менеджера'),
        ),
    ]