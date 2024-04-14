from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from taggit.models import TaggedItem
from django.contrib.contenttypes.models import ContentType

from apps.blog.models import Article, Project
from apps.blog.serializers import ArticleSerializer, ProjectSerializer, TagSerializer


class ArticleListView(APIView):

    @swagger_auto_schema(operation_description="List all articles",
                         tags=['Article'],
                         responses={200: ArticleSerializer(many=True)})
    def get(self, request, **kwargs):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ArticleSerializer,
                         operation_description="Create a new article",
                         tags=['Article'],
                         responses={201: ArticleSerializer(many=False)})
    def post(self, request):
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticleDetailView(APIView):

    @swagger_auto_schema(operation_description="Retrieve a specific article",
                         tags=['Article'],
                         responses={200: ArticleSerializer(many=True)})
    def get(self, request, pk, **kwargs):
        article = get_object_or_404(Article, pk=pk)
        serializer = ArticleSerializer(article)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ArticleSerializer,
                         operation_description="Update a specific article",
                         tags=['Article'],
                         responses={200: ArticleSerializer(many=False)})
    def put(self, request, pk, **kwargs):
        article = get_object_or_404(Article, pk=pk)
        serializer = ArticleSerializer(article, data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_description='Delete a specific article',
                         tags=['Article'],
                         responses={204: 'No content'})
    def delete(self, request, pk, **kwargs):
        article = get_object_or_404(Article, pk=pk)
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectListView(APIView):
    @swagger_auto_schema(operation_description='List all projects',
                         tags=['Project'],
                         responses={200: ProjectSerializer(many=True)})
    def get(self, request):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ProjectSerializer,
                         operation_description="Create a new project",
                         tags=['Project'],
                         responses={201: ProjectSerializer(many=False)})
    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailView(APIView):

    @swagger_auto_schema(operation_description='Retrieve a specific project',
                         tags=['Project'],
                         responses={200: ProjectSerializer(many=False)})
    def get(self, request, pk, **kwargs):
        project = get_object_or_404(Project, pk=pk)
        serializer = ProjectSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ProjectSerializer,
                         operation_description="Update a specific project",
                         tags=['Project'],
                         responses={200: ProjectSerializer(many=False)})
    def put(self, request, pk, **kwargs):
        project = get_object_or_404(Project, pk=pk)
        serializer = ProjectSerializer(project, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=ProjectSerializer,
                         operation_description='Update a specific project',
                         tags=['Project'],
                         responses={200: ProjectSerializer(many=False)})
    def delete(self, request, pk, **kwargs):
        project = get_object_or_404(Project, pk=pk)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagListView(APIView):

    def get(self, reqeust):
        queryset = TaggedItem.objects.all()
        print(queryset.first().object_id, ContentType.objects.get_for_model(Article))
        serializer = TagSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)