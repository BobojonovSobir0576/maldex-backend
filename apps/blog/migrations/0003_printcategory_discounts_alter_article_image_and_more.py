# Generated by Django 5.0.4 on 2024-08-05 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_gallery'),
    ]

    operations = [
        migrations.AddField(
            model_name='printcategory',
            name='discounts',
            field=models.JSONField(blank=True, null=True),
        ),
    ]