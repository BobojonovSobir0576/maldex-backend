from django.db import models


class Article(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    pub_date = models.DateTimeField('date published')
    image = models.ImageField(upload_to='articles/')

    def __str__(self):
        return self.title


class ArticleTag(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.title


class ProjectTag(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title
