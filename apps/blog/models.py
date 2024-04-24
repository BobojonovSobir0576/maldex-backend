from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from taggit.managers import TaggableManager
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.translation import gettext_lazy as _

from apps.product.models import Products


class Tag(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    name = models.CharField(_('name'), max_length=255)

    def __str__(self):
        return f'{self.name}'


class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('title'))
    body = CKEditor5Field(config_name='extends', verbose_name=_('content'))
    tags = models.ManyToManyField(Tag, verbose_name=_('article-tags'), related_name='articles')

    pub_date = models.DateTimeField(auto_now_add=True, verbose_name=_('date published'))
    image = models.ImageField(upload_to='articles/', verbose_name=_('image'))

    class Meta:
        ordering = ('-pub_date', 'title')
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')

    def __str__(self):
        return self.title


class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    tags = models.ManyToManyField(Tag, verbose_name=_('tags'))

    class Meta:
        ordering = ('title',)
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')

    def __str__(self):
        return self.title


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_images')
    image = models.ImageField(upload_to='projects/', verbose_name=_('image'))

    def __str__(self):
        return self.project.title


class ProjectProduct(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='project')


class FAQ(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    type = models.CharField(max_length=10, choices=(('home', 'home'), ('other', 'other')))
    order = models.PositiveSmallIntegerField(blank=True)

    def save(self, *args, **kwargs):
        if not self.order:
            last_instance = FAQ.objects.all().filter(type=self.type).last()
            order = 1 if not last_instance else int(last_instance.order) + 1
            self.order = order
        super(FAQ, self).save(*args, **kwargs)

    class Meta:
        ordering = ('type', 'order', 'title')
        verbose_name = _('FAQ')
        verbose_name_plural = _('FAQs')

    def __str__(self):
        return self.title


class PrintCategory(models.Model):
    title = models.CharField(max_length=200)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='print-categories/', null=True, blank=True)
    content = CKEditor5Field(config_name='extends', null=True, blank=True)
    requirement = CKEditor5Field(config_name='extends', null=True, blank=True)

    class Meta:
        ordering = ('title',)
        verbose_name = _('Print Category')
        verbose_name_plural = _('Print Categories')

    def __str__(self):
        return self.title
