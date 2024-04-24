from rest_framework import serializers
from taggit.models import TaggedItem

from apps.blog.models import Article, Project, FAQ, PrintCategory


class ArticleSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'title', 'body', 'tags', 'image', 'pub_date']

    def get_tags(self, obj):
        print([tag.name for tag in obj.tags.all()])
        return [tag.name for tag in obj.tags.all()]


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
