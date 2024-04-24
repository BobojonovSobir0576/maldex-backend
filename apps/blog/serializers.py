from django.shortcuts import get_object_or_404
from rest_framework import serializers
from taggit.models import TaggedItem

from apps.blog.models import Article, Project, FAQ, PrintCategory, Tag, ProjectImage, ProjectProduct
from apps.product.api.serializers import ProductListSerializers
from apps.product.models import Products


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
    products = serializers.SerializerMethodField(read_only=True)
    tags = serializers.SerializerMethodField(read_only=True)
    images = serializers.ListField(write_only=True)
    images_set = serializers.SerializerMethodField(read_only=True)
    product_ids = serializers.ListField(write_only=True)

    class Meta:
        model = Project
        fields = '__all__'

    def create(self, validated_data):
        images = validated_data.pop('images')
        product_ids = validated_data.pop('product_ids')
        project = Project.objects.create(**validated_data)
        for image in images:
            image_file = image.pop('image')[0]
            ProjectImage.objects.create(project=project, image=image_file)

        product_ids = list(map(int, product_ids[0].split(',')))
        for product_id in product_ids:
            product = get_object_or_404(Products, id=product_id)
            ProjectProduct.objects.create(project=project, product=product)

        return project

    def get_images_set(self, obj):
        images = []
        request = self.context['request']
        for image in  obj.project_images.all().values_list('image', flat=True):
            images.append(request.build_absolute_uri(image[0]))
        return images

    def get_tags(self, obj):
        return [tag['name'] for tag in obj.tags.all().values('name')]

    def get_products(self, obj):
        products = Products.objects.filter(project__project=obj)
        return ProductListSerializers(products, many=True).data


class FAQSerializer(serializers.ModelSerializer):

    class Meta:
        model = FAQ
        fields = '__all__'


class PrintCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = PrintCategory
        fields = '__all__'
