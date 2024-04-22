from django.contrib import admin

from apps.blog.models import Article, Project, FAQ, PrintCategory


class FAQAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'order']
    search_fields = ['title']
    fields = ['title', 'type', 'body']
    list_filter = ['type']


admin.site.register(Article)
admin.site.register(Project)
admin.site.register(FAQ, FAQAdmin)
admin.site.register(PrintCategory)
