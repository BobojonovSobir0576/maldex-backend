# Generated by Django 5.0.4 on 2024-06-13 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_productcategories_seo_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='added_recently',
            field=models.BooleanField(default=True),
        ),
    ]
