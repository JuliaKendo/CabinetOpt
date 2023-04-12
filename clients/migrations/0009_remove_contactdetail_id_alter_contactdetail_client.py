# Generated by Django 4.1.7 on 2023-04-11 10:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0008_alter_client_updated_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contactdetail',
            name='id',
        ),
        migrations.AlterField(
            model_name='contactdetail',
            name='client',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='contact_details', serialize=False, to='clients.client', verbose_name='Клиент'),
        ),
    ]