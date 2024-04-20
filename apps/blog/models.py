from django.db import models
from taggit.managers import TaggableManager
from ckeditor.fields import RichTextField


class Article(models.Model):
    title = models.CharField(max_length=200)
    body = RichTextField()
    tags = TaggableManager()

    pub_date = models.DateTimeField('date published', auto_now_add=True)
    image = models.ImageField(upload_to='articles/')

    def __str__(self):
        return self.title


class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    tags = TaggableManager()

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


class PrintCategory(models.Model):
    title = models.CharField(max_length=200)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='print-categories/', null=True, blank=True)
    content = RichTextField(null=True, blank=True)
    requirement = RichTextField(null=True, blank=True)
