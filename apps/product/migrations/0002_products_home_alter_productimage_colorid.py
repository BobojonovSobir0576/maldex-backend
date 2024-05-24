# Generated by Django 5.0.4 on 2024-05-23 12:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='home',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='colorID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='product.colors', verbose_name='Цвета'),
        ),
    ]