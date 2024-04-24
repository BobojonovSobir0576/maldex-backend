# Generated by Django 5.0.4 on 2024-04-23 09:53

import django_ckeditor_5.fields
import taggit.managers
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_alter_article_body'),
        ('taggit', '0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='article',
            options={'ordering': ('-pub_date', 'title'), 'verbose_name': 'Article', 'verbose_name_plural': 'Articles'},
        ),
        migrations.AlterModelOptions(
            name='faq',
            options={'ordering': ('type', 'order', 'title'), 'verbose_name': 'FAQ', 'verbose_name_plural': 'FAQs'},
        ),
        migrations.AlterModelOptions(
            name='printcategory',
            options={'ordering': ('title',), 'verbose_name': 'Print Category', 'verbose_name_plural': 'Print Categories'},
        ),
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ('title',), 'verbose_name': 'Project', 'verbose_name_plural': 'Projects'},
        ),
        migrations.AlterField(
            model_name='article',
            name='body',
            field=django_ckeditor_5.fields.CKEditor5Field(verbose_name='content'),
        ),
        migrations.AlterField(
            model_name='article',
            name='image',
            field=models.ImageField(upload_to='articles/', verbose_name='image'),
        ),
        migrations.AlterField(
            model_name='article',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='tags'),
        ),
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.CharField(max_length=200, verbose_name='title'),
        ),
    ]