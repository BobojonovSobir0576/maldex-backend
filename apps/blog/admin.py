from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe

from apps.blog.models import Article, Project, FAQ, PrintCategory, Tag, ProjectImage, LinkTag, Gallery, \
    PrintCategoryImage


# Customizing the admin interface for FAQs
class FAQAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'order']
    search_fields = ['title']
    fields = ['title', 'type', 'body']
    list_filter = ['type']


# Customizing the admin interface for Articles
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title', 'body']
    fields = ['title', 'body', 'tags', 'image']
    list_filter = ['tags']
    filter_horizontal = ['tags']


# Customizing the admin interface for Tags
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'content_type']
    search_fields = ['name']
    fields = ['name', 'content_type']
    list_filter = ['content_type']

    # Filtering content types for Tags to only include those from the 'blog' app
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'content_type':
            kwargs['queryset'] = ContentType.objects.filter(app_label='blog')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(LinkTag)
class LinkAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'order']
    search_fields = ['title']
    fields = ['title', 'category', 'link', 'order']
    readonly_fields = ('order',)


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ['id', 'data']
    search_fields = ['id']
    readonly_fields = ('data',)


class PrintCategoryImageInline(admin.TabularInline):
    model = PrintCategoryImage
    fields = ('_image', 'image',)
    readonly_fields = ('_image',)

    def _image(self, obj):
        image_url = obj.image.url
        html = mark_safe(f'<img src="{image_url}" width=70 height=70 style="object-fit: cover">')
        return html if image_url else ''

    _image.short_description = ''


@admin.register(PrintCategory)
class PrintCategoryAdmin(admin.ModelAdmin):
    inlines = [PrintCategoryImageInline]


admin.site.register(Article, ArticleAdmin)
admin.site.register(Project)
admin.site.register(FAQ, FAQAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ProjectImage)
