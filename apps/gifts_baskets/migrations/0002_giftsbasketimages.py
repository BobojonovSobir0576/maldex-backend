# Generated by Django 5.0.4 on 2024-04-20 13:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gifts_baskets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GiftsBasketImages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('images', models.ImageField(blank=True, null=True, upload_to='gift_basket/')),
                ('gift_basket', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                                  related_name='basket_images', to='gifts_baskets.giftsbaskets')),
            ],
            options={
                'verbose_name': 'Подарочные наборы изображения',
                'verbose_name_plural': 'Подарочные наборы изображения',
                'db_table': 'gifts_basket_image',
            },
        ),
    ]

