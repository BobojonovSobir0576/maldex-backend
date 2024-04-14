from rest_framework import serializers
from taggit.models import TaggedItem

from apps.blog.models import Article, Project


class ArticleSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = '__all__'

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaggedItem
        fields = '__all__'
