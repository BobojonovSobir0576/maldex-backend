from django.db import models
from taggit.managers import TaggableManager


class Tag(models.Model):
    name = models.CharField(max_length=100)



class Article(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    tags = TaggableManager()

    pub_date = models.DateTimeField('date published')
    image = models.ImageField(upload_to='articles/')

    def __str__(self):
        return self.title



class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    tags = TaggableManager()

    def __str__(self):
        return self.title
