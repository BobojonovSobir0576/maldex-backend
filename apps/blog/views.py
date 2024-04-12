from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.blog.models import Article, ArticleTag, Project, ProjectTag
from apps.blog.serializers import ArticleSerializer, ArticleTagSerializer, ProjectSerializer, ProjectTagSerializer


class ArticleListView(APIView):

    @swagger_auto_schema(operation_description="List all articles",
                         tags=['Article'],
                         responses={200: ArticleSerializer(many=True)})
    def get(self, request, **kwargs):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
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


class ArticleTagListView(APIView):

    @swagger_auto_schema(operation_description='List all articles tags',
                         tags=['Article Tag'],
                         responses={200: ArticleTagSerializer(many=True)})
    def get(self, request, **kwargs):
        article_categories = ArticleTagSerializer.objects.all()
        serializer = ArticleTagSerializer(article_categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ArticleTagSerializer,
                         operation_description='Add a new article tag',
                         tags=['Article Tag'],
                         responses={201: ArticleTagSerializer(many=False)})
    def post(self, request):
        serializer = ArticleTagSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


class ProjectTagListView(APIView):

    @swagger_auto_schema(operation_description='List all projects tags',
                         tags=['Project Tag'],
                         responses={200: ProjectTagSerializer(many=True)})
    def get(self, request, **kwargs):
        project_tags = ProjectTag.objects.all()
        serializer = ProjectTagSerializer(project_tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ProjectTagSerializer,
                         operation_description='Add a new project tag',
                         tags=['Project Tag'],
                         responses={201: ProjectTagSerializer(many=False)})
    def post(self, request):
        serializer = ProjectTagSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
