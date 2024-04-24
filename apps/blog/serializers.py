from rest_framework import serializers
from taggit.models import TaggedItem

from apps.blog.models import Article, Project, FAQ, PrintCategory, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag


class ArticleSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'title', 'body', 'tags', 'image', 'pub_date']

    def get_tags(self, obj):
        return [tag['name'] for tag in obj.tags.all().values('name')]


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = '__all__'


class FAQSerializer(serializers.ModelSerializer):

    class Meta:
        model = FAQ
        fields = '__all__'


class PrintCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = PrintCategory
        fields = '__all__'
