# Generated by Django 5.0.4 on 2024-05-03 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0009_products_prints'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='quantity',
            field=models.CharField(blank=True, max_length=252, null=True),
        ),
    ]