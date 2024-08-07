from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.blog.models import Article, Project, FAQ, PrintCategory, Tag, LinkTag, LinkTagCategory, Gallery
from apps.blog.serializers import ArticleSerializer, ProjectSerializer, FAQSerializer, PrintCategorySerializer, \
    LinkSerializer, LinkCategorySerializer, GallerySerializer
from utils.responses import success_response, success_created_response, bad_request_response, success_deleted_response


class ArticleListView(APIView):
    """
    API endpoint to list and create articles.
    """
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_description="List all articles",
        tags=['Article'],
        responses={200: ArticleSerializer(many=True)}
    )
    def get(self, request):
        """
        Get all articles.
        """
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True, context={'request': request})
        return success_response(serializer.data)

    @swagger_auto_schema(
        request_body=ArticleSerializer,
        operation_description="Create a new article",
        tags=['Article'],
        responses={201: ArticleSerializer(many=False)}
    )
    def post(self, request):
        """
        Create a new article.
        """
        serializer = ArticleSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_created_response(serializer.data)
        return bad_request_response(serializer.errors)


class ArticleDetailView(APIView):
    """
    API endpoint to retrieve, update, and delete a specific article.
    """
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_description="Retrieve a specific article",
        tags=['Article'],
        responses={200: ArticleSerializer(many=False)}
    )
    def get(self, request, pk, **kwargs):
        """
        Retrieve a specific article.
        """
        article = get_object_or_404(Article, pk=pk)
        serializer = ArticleSerializer(article, context={'request': request})
        return success_response(serializer.data)

    @swagger_auto_schema(
        request_body=ArticleSerializer,
        operation_description="Update a specific article",
        tags=['Article'],
        responses={200: ArticleSerializer(many=False)}
    )
    def put(self, request, pk, **kwargs):
        """
        Update a specific article.
        """
        article = get_object_or_404(Article, pk=pk)
        serializer = ArticleSerializer(article, data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response(serializer.data)
        return bad_request_response(serializer.errors)

    @swagger_auto_schema(
        operation_description="Delete a specific article",
        tags=['Article'],
        responses={204: 'No content'}
    )
    def delete(self, request, pk, **kwargs):
        """
        Delete a specific article.
        """
        article = get_object_or_404(Article, pk=pk)
        article.delete()
        return success_deleted_response('deleted')


class ProjectListView(APIView):
    """
    API endpoint to list and create projects.
    """
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter('tag_id', openapi.IN_QUERY,
                                             description="Tag name",
                                             type=openapi.TYPE_INTEGER)],
        operation_description="List all projects",
        tags=['Project'],
        responses={200: ProjectSerializer(many=True)}
    )
    def get(self, request):
        """
        Get all projects.
        """
        tag_id = request.GET.get('tag_id', None)
        projects = Project.objects.all()
        projects = projects.filter(tags__id=tag_id) if tag_id else projects
        serializer = ProjectSerializer(projects, many=True, context={'request': request})
        return success_response(serializer.data)

    @swagger_auto_schema(
        request_body=ProjectSerializer,
        operation_description="Create a new project",
        tags=['Project'],
        responses={201: ProjectSerializer(many=False)}
    )
    def post(self, request):
        """
        Create a new project.
        """
        serializer = ProjectSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_created_response(serializer.data)
        return bad_request_response(serializer.errors)


class ProjectDetailView(APIView):
    """
    API endpoint to retrieve, update, and delete a specific project.
    """
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_description="Retrieve a specific project",
        tags=['Project'],
        responses={200: ProjectSerializer(many=False)}
    )
    def get(self, request, pk, **kwargs):
        """
        Retrieve a specific project.
        """
        project = get_object_or_404(Project, pk=pk)
        serializer = ProjectSerializer(project, context={'request': request})
        return success_response(serializer.data)

    @swagger_auto_schema(
        request_body=ProjectSerializer,
        operation_description="Update a specific project",
        tags=['Project'],
        responses={200: ProjectSerializer(many=False)}
    )
    def put(self, request, pk, **kwargs):
        """
        Update a specific project.
        """
        project = get_object_or_404(Project, pk=pk)
        serializer = ProjectSerializer(project, data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response(serializer.data)
        return bad_request_response(serializer.errors)

    @swagger_auto_schema(
        operation_description="Delete a specific project",
        tags=['Project'],
        responses={204: 'No content'}
    )
    def delete(self, request, pk, **kwargs):
        """
        Delete a specific project.
        """
        project = get_object_or_404(Project, pk=pk)
        project.delete()
        return success_deleted_response('deleted')


@swagger_auto_schema(tags=['Article'],
                     operation_description='Get all article tags',
                     method='GET')
@api_view(['GET'])
def get_article_tags(request):
    tags = list(Tag.objects.filter(content_type=ContentType.objects.get_for_model(Article)).values('id', 'name'))
    return success_response(tags)


@swagger_auto_schema(tags=['Project'],
                     operation_description='Get all project tags',
                     method='GET')
@api_view(['GET'])
def get_project_tags(request):
    tags = list(Tag.objects.filter(content_type=ContentType.objects.get_for_model(Project)).values('id', 'name'))
    return success_response(tags)


class FAQListView(APIView):
    """
    API endpoint to list and create FAQs.
    """
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_description="List all FAQs",
        tags=['FAQ'],
        manual_parameters=[
            openapi.Parameter(
                'type',
                openapi.IN_QUERY,
                description='Type of FAQ [home, other]',
                type=openapi.TYPE_STRING,
                choices=[('home', 'home'), ('other', 'other')]
            )
        ],
        responses={200: FAQSerializer(many=True)}
    )
    def get(self, request):
        """
        Get all FAQs, optionally filtered by type.
        """
        faq_type = request.query_params.get('type', None)
        faqs = FAQ.objects.filter(type=faq_type)
        serializer = FAQSerializer(faqs, many=True)
        return success_response(serializer.data)

    @swagger_auto_schema(
        request_body=FAQSerializer,
        operation_description="Create a new FAQ",
        tags=['FAQ'],
        responses={201: FAQSerializer()}
    )
    def post(self, request):
        """
        Create a new FAQ.
        """
        serializer = FAQSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_created_response(serializer.data)
        return bad_request_response(serializer.errors)


class FAQDetailView(APIView):
    """
    API endpoint to retrieve, update, and delete a specific FAQ.
    """
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_description="Retrieve a specific FAQ",
        tags=['FAQ'],
        responses={200: FAQSerializer()}
    )
    def get(self, request, faq_id, **kwargs):
        """
        Retrieve a specific FAQ.
        """
        faq = get_object_or_404(FAQ, id=faq_id)
        serializer = FAQSerializer(faq)
        return success_response(serializer.data)

    @swagger_auto_schema(
        request_body=FAQSerializer,
        operation_description="Update a specific FAQ",
        tags=['FAQ'],
        responses={200: FAQSerializer()}
    )
    def put(self, request, faq_id, **kwargs):
        """
        Update a specific FAQ.
        """
        faq = get_object_or_404(FAQ, id=faq_id)
        serializer = FAQSerializer(faq, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response(serializer.data)
        return bad_request_response(serializer.errors)

    @swagger_auto_schema(
        operation_description="Delete a specific FAQ",
        tags=['FAQ'],
        responses={204: 'No content'}
    )
    def delete(self, request, faq_id, **kwargs):
        """
        Delete a specific FAQ.
        """
        faq = get_object_or_404(FAQ, id=faq_id)
        faq.delete()
        return success_deleted_response('deleted')


class PrintCategoryListView(APIView):
    """
    API endpoint to list and create print categories.
    """
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_description="List all print categories",
        tags=['Print Category'],
        responses={200: PrintCategorySerializer(many=True)}
    )
    def get(self, request):
        """
        Get all print categories.
        """
        categories = PrintCategory.objects.all()
        serializer = PrintCategorySerializer(categories, many=True, context={'request': request})
        return success_response(serializer.data)

    @swagger_auto_schema(
        request_body=PrintCategorySerializer,
        operation_description="Create a new print category",
        tags=['Print Category'],
        responses={201: PrintCategorySerializer()}
    )
    def post(self, request):
        """
        Create a new print category.
        """
        serializer = PrintCategorySerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_created_response(serializer.data)
        return bad_request_response(serializer.errors)


class PrintCategoryDetailView(APIView):
    """
    API endpoint to retrieve, update, and delete a specific print category.
    """
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_description="Retrieve a specific print category",
        tags=['Print Category'],
        responses={200: PrintCategorySerializer()}
    )
    def get(self, request, category_id, **kwargs):
        """
        Retrieve a specific print category.
        """
        category = get_object_or_404(PrintCategory, id=category_id)
        serializer = PrintCategorySerializer(category, context={'request': request})
        return success_response(serializer.data)

    @swagger_auto_schema(
        request_body=PrintCategorySerializer,
        operation_description="Update a specific print category",
        tags=['Print Category'],
        responses={200: PrintCategorySerializer()}
    )
    def put(self, request, category_id, **kwargs):
        """
        Update a specific print category.
        """
        category = get_object_or_404(PrintCategory, id=category_id)
        serializer = PrintCategorySerializer(category, data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response(serializer.data)
        return bad_request_response(serializer.errors)

    @swagger_auto_schema(
        operation_description="Delete a specific print category",
        tags=['Print Category'],
        responses={204: 'No content'}
    )
    def delete(self, request, category_id, **kwargs):
        """
        Delete a specific print category.
        """
        category = get_object_or_404(PrintCategory, id=category_id)
        category.delete()
        return success_deleted_response('deleted')


class LinkList(APIView):
    """
    API endpoint to list and create link tags.
    """
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_description="List all link tags",
        tags=['Link Tag'],
        responses={200: LinkSerializer(many=True)}
    )
    def get(self, request):
        """
        Get all print link tags.
        """
        categories = LinkTag.objects.all()
        serializer = LinkSerializer(categories, many=True, context={'request': request})
        return success_response(serializer.data)

    @swagger_auto_schema(
        request_body=LinkSerializer,
        operation_description="Create a link tag",
        tags=['Link Tag'],
        responses={201: LinkSerializer()}
    )
    def post(self, request):
        """
        Create a new link tag.
        """
        serializer = LinkSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_created_response(serializer.data)
        return bad_request_response(serializer.errors)


class LinkDetail(APIView):
    """
    API endpoint to retrieve, update, and delete a specific print category.
    """
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_description="Retrieve a specific print category",
        tags=['Link Tag'],
        responses={200: LinkSerializer()}
    )
    def get(self, request, link_id, **kwargs):
        """
        Retrieve a specific print category.
        """
        category = get_object_or_404(LinkTag, id=link_id)
        serializer = LinkSerializer(category, context={'request': request})
        return success_response(serializer.data)

    @swagger_auto_schema(
        request_body=LinkSerializer,
        operation_description="Update a specific print category",
        tags=['Link Tag'],
        responses={200: LinkSerializer()}
    )
    def put(self, request, link_id, **kwargs):
        """
        Update a specific print category.
        """
        category = get_object_or_404(LinkTag, id=link_id)
        serializer = LinkSerializer(category, data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response(serializer.data)
        return bad_request_response(serializer.errors)

    @swagger_auto_schema(
        operation_description="Delete a specific print category",
        tags=['Link Tag'],
        responses={204: 'No content'}
    )
    def delete(self, request, link_id, **kwargs):
        """
        Delete a specific print category.
        """
        category = get_object_or_404(LinkTag, id=link_id)
        category.delete()
        return success_deleted_response('deleted')


class LinkCategoryList(APIView):
    """
    API endpoint to list and create link tags.
    """
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_description="List all link tags",
        tags=['Link Tag Category'],
        responses={200: LinkCategorySerializer(many=True)}
    )
    def get(self, request):
        """
        Get all print link tags.
        """
        categories = LinkTagCategory.objects.all()
        serializer = LinkCategorySerializer(categories, many=True, context={'request': request})
        return success_response(serializer.data)

    @swagger_auto_schema(
        request_body=LinkCategorySerializer,
        operation_description="Create a link tag",
        tags=['Link Tag Category'],
        responses={201: LinkCategorySerializer()}
    )
    def post(self, request):
        """
        Create a new link tag.
        """
        serializer = LinkCategorySerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_created_response(serializer.data)
        return bad_request_response(serializer.errors)


class LinkCategoryDetail(APIView):
    """
    API endpoint to retrieve, update, and delete a specific print category.
    """
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_description="Retrieve a specific print category",
        tags=['Link Tag Category'],
        responses={200: LinkCategorySerializer()}
    )
    def get(self, request, cat_id, **kwargs):
        """
        Retrieve a specific print category.
        """
        category = get_object_or_404(LinkTagCategory, id=cat_id)
        serializer = LinkCategorySerializer(category, context={'request': request})
        return success_response(serializer.data)

    @swagger_auto_schema(
        request_body=LinkCategorySerializer,
        operation_description="Update a specific print category",
        tags=['Link Tag Category'],
        responses={200: LinkCategorySerializer()}
    )
    def put(self, request, cat_id, **kwargs):
        """
        Update a specific print category.
        """
        category = get_object_or_404(LinkTagCategory, id=cat_id)
        serializer = LinkCategorySerializer(category, data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response(serializer.data)
        return bad_request_response(serializer.errors)

    @swagger_auto_schema(
        operation_description="Delete a specific print category",
        tags=['Link Tag Category'],
        responses={204: 'No content'}
    )
    def delete(self, request, cat_id, **kwargs):
        """
        Delete a specific print category.
        """
        category = get_object_or_404(LinkTagCategory, id=cat_id)
        category.delete()
        return success_deleted_response('deleted')


class GalleryList(APIView):
    """
    API endpoint to list and create link tags.
    """
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_description="List all gallery data",
        tags=['Gallery'],
        responses={200: GallerySerializer(many=True)}
    )
    def get(self, request):
        """
        Get all print link tags.
        """
        categories = Gallery.objects.all()
        serializer = GallerySerializer(categories, many=True, context={'request': request})
        return success_response(serializer.data)

    @swagger_auto_schema(
        request_body=GallerySerializer,
        operation_description="Create a gallery data",
        tags=['Gallery'],
        responses={201: GallerySerializer()}
    )
    def post(self, request):
        """
        Create a new link tag.
        """
        serializer = GallerySerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_created_response(serializer.data)
        return bad_request_response(serializer.errors)


class GalleryDetail(APIView):
    """
    API endpoint to retrieve, update, and delete a specific print category.
    """
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_description="Retrieve a gallery data",
        tags=['Gallery'],
        responses={200: GallerySerializer()}
    )
    def get(self, request, gallery_id, **kwargs):
        """
        Retrieve a specific print category.
        """
        category = get_object_or_404(Gallery, id=gallery_id)
        serializer = GallerySerializer(category, context={'request': request})
        return success_response(serializer.data)

    @swagger_auto_schema(
        request_body=GallerySerializer,
        operation_description="Update a gallery data",
        tags=['Gallery'],
        responses={200: GallerySerializer()}
    )
    def put(self, request, gallery_id, **kwargs):
        """
        Update a specific print category.
        """
        gallery = get_object_or_404(Gallery, id=gallery_id)
        serializer = GallerySerializer(gallery, data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return success_response(serializer.data)
        return bad_request_response(serializer.errors)

    @swagger_auto_schema(
        operation_description="Delete a gallery data",
        tags=['Gallery'],
        responses={204: 'No content'}
    )
    def delete(self, request, gallery_id, **kwargs):
        """
        Delete a specific print category.
        """
        gallery = get_object_or_404(Gallery, id=gallery_id)
        gallery.delete()
        return success_deleted_response('deleted')
