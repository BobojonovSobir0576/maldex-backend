from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from taggit.models import TaggedItem
from django.contrib.contenttypes.models import ContentType

from apps.blog.models import Article, Project, FAQ, PrintCategory
from apps.blog.serializers import ArticleSerializer, ProjectSerializer, TagSerializer, FAQSerializer, \
    PrintCategorySerializer


class ArticleListView(APIView):
    permission_classes = (AllowAny,)

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
    permission_classes = (AllowAny,)

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
    permission_classes = (AllowAny,)

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
    permission_classes = (AllowAny,)

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
    permission_classes = (AllowAny,)

    def get(self, reqeust):
        queryset = TaggedItem.objects.all()
        print(queryset.first().object_id, ContentType.objects.get_for_model(Article))
        serializer = TagSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FAQListView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = FAQSerializer

    @swagger_auto_schema(operation_description='List all FAQs',
                         manual_parameters=[openapi.Parameter(
                             'type',
                             openapi.IN_QUERY,
                             description='Type of FAQ [home, other]',
                             type=openapi.TYPE_STRING,
                             choices=[('home', 'home'), ('other', 'other')]
                         )],
                         tags=['FAQ'],
                         responses={200: FAQSerializer(many=True)})
    def get(self, request):
        faq_type = request.query_params.get('type', None)
        faqs = FAQ.objects.filter(type=faq_type)
        serializer = FAQSerializer(faqs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description='Create a new FAQ',
                         tags=['FAQ'],
                         request_body=FAQSerializer,
                         responses={200: FAQSerializer})
    def post(self, request, *args, **kwargs):
        serializer = FAQSerializer(data=request.data, context={request: request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FAQDetailView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = FAQSerializer

    @swagger_auto_schema(operation_description='Get a FAQ',
                         tags=['FAQ'],
                         responses={200: FAQSerializer})
    def get(self, request, faq_id, *args, **kwargs):
        faq = get_object_or_404(FAQ, id=faq_id)
        serializer = FAQSerializer(faq)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description='Update a FAQ',
                         tags=['FAQ'],
                         request_body=FAQSerializer,
                         responses={200: FAQSerializer})
    def put(self, request, faq_id, *args, **kwargs):
        faq = get_object_or_404(FAQ, id=faq_id)
        serializer = FAQSerializer(faq, data=request.data, context={request: request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_description='Delete a FAQ',
                         tags=['FAQ'],)
    def delete(self, request, faq_id, *args, **kwargs):
        faq = get_object_or_404(FAQ, id=faq_id)
        faq.delete()

        # reorder faqs
        faqs = FAQ.objects.filter(type=faq.type)
        for i in range(faqs.count()):
            faq_model = faqs[i]
            faq_model.order = i + 1
            faq_model.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class PrintCategoryListView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = PrintCategorySerializer

    @swagger_auto_schema(operation_description='List a print categories',
                         tags=['Print Category'],
                         responses={200: PrintCategorySerializer(many=True)})
    def get(self, request):
        categories = PrintCategory.objects.all()
        serializer = PrintCategorySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description='Create a new category',
                         tags=['Print Category'],
                         request_body=PrintCategorySerializer,
                         responses={200: PrintCategorySerializer})
    def post(self, request, *args, **kwargs):
        serializer = PrintCategorySerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PrintCategoryDetailView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = PrintCategorySerializer

    @swagger_auto_schema(operation_description='Get a category',
                         tags=['Print Category'],
                         responses={200: PrintCategorySerializer})
    def get(self, request, category_id, *args, **kwargs):
        category = get_object_or_404(PrintCategory, id=category_id)
        serializer = self.serializer_class(category, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description='Update a category',
                         tags=['Print Category'],
                         request_body=PrintCategorySerializer,
                         responses={200: PrintCategorySerializer})
    def put(self, request, category_id, *args, **kwargs):
        category = get_object_or_404(PrintCategory, id=category_id)
        serializer = self.serializer_class(category, data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_description='Delete a category',
                         tags=['Print Category'])
    def delete(self, request, category_id, *args, **kwargs):
        category = get_object_or_404(PrintCategory, id=category_id)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
