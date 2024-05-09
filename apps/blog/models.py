from django.contrib.contenttypes.models import ContentType
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.translation import gettext_lazy as _

from apps.product.models import Products


# Model for tags
class Tag(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name=_('Тип содержимого'))
    name = models.CharField(max_length=255, verbose_name=_('название'))

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'blog_tag'
        ordering = ('name',)
        verbose_name = _('тег')
        verbose_name_plural = _('теги')


# Model for articles
class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('заголовок'))
    body = CKEditor5Field(config_name='extends', verbose_name=_('содержание'))
    tags = models.ManyToManyField(Tag, verbose_name=_('теги статей'), related_name='articles')
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name=_('дата публикации'))
    image = models.ImageField(upload_to='articles/', verbose_name=_('изображение'))
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name=_('date published'))
    image = models.ImageField(upload_to='articles/', verbose_name=_('image'), null=False)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'article'
        ordering = ('-pub_date', 'title')
        verbose_name = _('Статья')
        verbose_name_plural = _('Статьи')


# Model for projects
class Project(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('заголовок'))
    description = models.TextField(verbose_name=_('описание'))
    tags = models.ManyToManyField(Tag, verbose_name=_('теги проекта'))

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'project'
        ordering = ('title',)
        verbose_name = _('Проект')
        verbose_name_plural = _('Проекты')


# Model for project images
class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name=_('проект'),
                                related_name='project_images')
    image = models.ImageField(upload_to='projects/', verbose_name=_('изображение'))

    def __str__(self):
        return self.project.title

    class Meta:
        db_table = 'project_image'
        ordering = ('project',)
        verbose_name = _('Изображение проекта')
        verbose_name_plural = _('Изображения проекта')


# Model for project products
class ProjectProduct(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='products', verbose_name=_('проект'))
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='project', verbose_name=_('продукт'))

    def __str__(self):
        return f'{self.project}: {self.product}'

    class Meta:
        db_table = 'project_product'
        ordering = ('project', 'product')
        verbose_name = _('Продукт проекта')
        verbose_name_plural = _('Продукты проекта')


# Model for frequently asked questions (FAQs)
class FAQ(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('заголовок'))
    body = models.TextField(verbose_name=_('описание'))
    type = models.CharField(max_length=10, choices=(('home', 'home'), ('other', 'other')), verbose_name=_("тип"))
    order = models.PositiveSmallIntegerField(blank=True, verbose_name=_('очередь'))

    def save(self, *args, **kwargs):
        # Auto-generate order if not provided
        if not self.order:
            last_instance = FAQ.objects.all().filter(type=self.type).last()
            order = 1 if not last_instance else int(last_instance.order) + 1
            self.order = order
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'faq'
        ordering = ('type', 'order', 'title')
        verbose_name = _('Часто задаваемые вопросы')
        verbose_name_plural = _('Часто задаваемые вопросы')

    def __str__(self):
        return self.title


# Model for print categories
class PrintCategory(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('заголовок'))
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE,
                               verbose_name=_('родительская категория'))
    image = models.ImageField(upload_to='print-categories/', null=True, blank=True, verbose_name=_('изображение'))
    content = CKEditor5Field(config_name='extends', null=True, blank=True, verbose_name=_('содержание'))
    requirement = CKEditor5Field(config_name='extends', null=True, blank=True, verbose_name=_('требование'))

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'print_category'
        ordering = ('title',)
        verbose_name = _('Категория печати')
        verbose_name_plural = _('Категории печати')


class LinkTagCategory(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('заголовок'))

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'link_tag_category'
        ordering = ('title',)


class LinkTag(models.Model):
    title = models.CharField(max_length=100)
    link = models.URLField()
    category = models.ForeignKey(LinkTagCategory, on_delete=models.CASCADE, related_name='tags')
    order = models.PositiveSmallIntegerField(default=1, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'link_tag'
        ordering = ('order',)

    def save(self, *args, **kwargs):
        if not self.order:
            last_instance = LinkTag.objects.all().last()
            order = 1 if not last_instance else int(last_instance.order) + 1
            self.order = order
        super().save(*args, **kwargs)

