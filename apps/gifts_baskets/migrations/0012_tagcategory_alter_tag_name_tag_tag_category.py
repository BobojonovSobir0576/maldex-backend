# Generated by Django 5.0.4 on 2024-04-26 05:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gifts_baskets', '0011_alter_adminfiles_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='TagCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Тег категории',
                'verbose_name_plural': 'Тег категории',
                'db_table': 'teg_category',
            },
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Название тэга'),
        ),
        migrations.AddField(
            model_name='tag',
            name='tag_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='categoryTag', to='gifts_baskets.tagcategory'),
        ),
    ]