# Generated by Django 5.0.4 on 2024-05-05 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0010_products_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='article',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='Артикул'),
        ),
        migrations.AlterField(
            model_name='products',
            name='code',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='products',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Описания'),
        ),
        migrations.AlterField(
            model_name='products',
            name='is_hit',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='Хит?'),
        ),
        migrations.AlterField(
            model_name='products',
            name='is_new',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='Новый?'),
        ),
        migrations.AlterField(
            model_name='products',
            name='is_popular',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='Популярен?'),
        ),
        migrations.AlterField(
            model_name='products',
            name='material',
            field=models.CharField(blank=True, default='S-XXL', max_length=512, null=True, verbose_name='Материал'),
        ),
        migrations.AlterField(
            model_name='products',
            name='name',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='Название продукта'),
        ),
        migrations.AlterField(
            model_name='products',
            name='ondemand',
            field=models.BooleanField(blank=True, default=True, null=True),
        ),
        migrations.AlterField(
            model_name='products',
            name='price',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='Цена'),
        ),
        migrations.AlterField(
            model_name='products',
            name='price_type',
            field=models.CharField(blank=True, choices=[('RUB', 'RUB'), ('USD', 'USD')], default='RUB', max_length=10, null=True, verbose_name='Цена валюта'),
        ),
        migrations.AlterField(
            model_name='products',
            name='product_size',
            field=models.CharField(blank=True, default='S-XXL', max_length=256, null=True, verbose_name='Размер товара'),
        ),
    ]