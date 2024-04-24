from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from apps.blog.models import Article, Project, FAQ, PrintCategory, Tag


class FAQAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'order']
    search_fields = ['title']
    fields = ['title', 'type', 'body']
    list_filter = ['type']


class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title', 'body']
    fields = ['title', 'body', 'tags', 'image']
    list_filter = ['tags']
    filter_horizontal = ['tags']


class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'content_type']
    search_fields = ['name']
    fields = ['name', 'content_type']
    list_filter = ['content_type']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'content_type':
            kwargs['queryset'] = ContentType.objects.filter(app_label='blog')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Article, ArticleAdmin)
admin.site.register(Project)
admin.site.register(FAQ, FAQAdmin)
admin.site.register(PrintCategory)
admin.site.register(Tag, TagAdmin)
