from rest_framework import serializers

from apps.blog.models import Article, ArticleTag, Project, ProjectTag


class ArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = '__all__'


class ArticleTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = ArticleTag
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = '__all__'


class ProjectTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectTag
        fields = '__all__'
