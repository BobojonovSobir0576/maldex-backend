from django.contrib import admin

from apps.blog.models import Article, Project


admin.site.register(Article)
admin.site.register(Project)
