# Generated by Django 5.0.4 on 2024-07-17 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0003_alter_customuser_options_remove_customuser_about_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(max_length=128, null=True),
        ),
    ]