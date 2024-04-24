from django.db import models
from taggit.managers import TaggableManager
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.translation import gettext_lazy as _


class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('title'))
    body = CKEditor5Field(config_name='extends', verbose_name=_('content'))
    tags = TaggableManager(_('tags'))

    pub_date = models.DateTimeField(auto_now_add=True, verbose_name=_('date published'))
    image = models.ImageField(upload_to='articles/', verbose_name=_('image'), null=False)

    class Meta:
        ordering = ('-pub_date', 'title')
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')

    def __str__(self):
        return self.title


class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    tags = TaggableManager()

    class Meta:
        ordering = ('title',)
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')

    def __str__(self):
        return self.title


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
