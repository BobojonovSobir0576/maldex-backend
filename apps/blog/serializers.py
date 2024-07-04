from django.shortcuts import get_object_or_404
from rest_framework import serializers

from apps.blog.models import Article, Project, FAQ, PrintCategory, Tag, ProjectImage, ProjectProduct, LinkTag, \
    LinkTagCategory, Gallery
from apps.product.api.serializers import ProductListSerializers
from apps.product.models import Products


# Serializer for Tags
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag


# Serializer for Articles
class ArticleSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    tags = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False,)

    class Meta:
        model = Article
        fields = ['id', 'title', 'body', 'tags', 'image', 'pub_date']

    @staticmethod
    def get_tags(obj):
        # Retrieve tags associated with the article
        return [tag['name'] for tag in obj.tags.all().values('name')]


# Serializer for Projects
class ProjectSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField(read_only=True)
    tag_set = serializers.SerializerMethodField()
    images = serializers.ListField(write_only=True)
    images_set = serializers.SerializerMethodField(read_only=True)
    product_ids = serializers.ListField(write_only=True)
    tags = serializers.ListField(write_only=True)

    class Meta:
        model = Project
        fields = '__all__'

    def create(self, validated_data):
        # Create a new project with associated images and products
        images = validated_data.pop('images')
        product_ids = validated_data.pop('product_ids')
        tags = list(map(int, validated_data.pop('tags')[0].split(',')))
        project = Project.objects.create(**validated_data)

        # Add tags to the project
        for tag_id in tags:
            project.tags.add(Tag.objects.get(pk=tag_id))

        # Add images to the project
        for image in images:
            image_file = image.pop('image')[0]
            ProjectImage.objects.create(project=project, image=image_file)

        # Add products to the project
        product_ids = list(map(int, product_ids[0].split(',')))
        for product_id in product_ids:
            product = get_object_or_404(Products, id=product_id)
            ProjectProduct.objects.create(project=project, product=product)

        return project

    def get_images_set(self, obj):
        # Retrieve the absolute URLs of project images
        images = []
        request = self.context['request']

        for image in obj.project_images.all():
            images.append(request.build_absolute_uri(image.image.url))
        return images

    @staticmethod
    def get_tag_set(obj):
        # Retrieve tags associated with the project
        return [tag['name'] for tag in obj.tags.all().values('name')]

    def get_products(self, obj):
        # Retrieve products associated with the project
        products = Products.objects.filter(project__project=obj)
        return ProductListSerializers(products, many=True, context=self.context).data


# Serializer for FAQs
class FAQSerializer(serializers.ModelSerializer):

    class Meta:
        model = FAQ
        fields = '__all__'


# Serializer for Print Categories
class PrintCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = PrintCategory
        fields = '__all__'


class LinkCategorySerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    tags = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = LinkTagCategory
        fields = ['id', 'title', 'tags']

    @staticmethod
    def get_tags(obj):
        tags = obj.tags
        return LinkSerializer(tags, many=True).data


class LinkSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    link = serializers.URLField(required=False)
    category_id = serializers.IntegerField(write_only=True)
    category_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = LinkTag
        fields = ['id', 'title', 'link', 'category_id', 'category_name']
        
    @staticmethod
    def get_category_name(obj):
        category = obj.category
        return category.title

    def create(self, validated_data):
        category = get_object_or_404(LinkTagCategory, id=validated_data.pop('category_id'))
        return LinkTag.objects.create(category=category, **validated_data)

    def update(self, instance, validated_data):
        category_id = validated_data.pop('category_id')
        instance.category.id = category_id
        instance.save()
        return instance


class GallerySerializer(serializers.ModelSerializer):

    class Meta:
        model = Gallery
        fields = '__all__'
