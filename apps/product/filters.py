from string import punctuation
from django.contrib.admin import SimpleListFilter
from django.db.models import Q
from django_filters import rest_framework as filters
from django.db.models import F, Func, Value
from django.db.models.functions import Replace
from apps.product.models import ProductCategories, Products


class SubCategoryListFilter(SimpleListFilter):
    """Custom filter for subcategories."""
    title = 'subcategory'
    parameter_name = 'subcategory'

    def lookups(self, request, model_admin):
        """Return a list of tuples for the filter options."""
        subcategories = ProductCategories.objects.filter(parent__isnull=False, parent__parent__isnull=True)
        return [(subcategory.id, subcategory.name) for subcategory in subcategories]

    def queryset(self, request, queryset):
        """Return the filtered queryset based on the selected subcategory."""
        if self.value():
            return queryset.filter(parent_id=self.value())
        return queryset


class MainCategoryListFilter(SimpleListFilter):
    """Custom filter for main categories."""
    title = 'main category'
    parameter_name = 'main_category'

    def lookups(self, request, model_admin):
        """Return a list of tuples for the filter options."""
        main_categories = ProductCategories.objects.filter(parent__isnull=True)
        return [(cat.id, cat.name) for cat in main_categories]

    def queryset(self, request, queryset):
        """Return the filtered queryset based on the selected main category."""
        if self.value():
            return queryset.filter(parent__id=self.value())
        return queryset


class ProductCategoryFilter(filters.FilterSet):
    """FilterSet for filtering product categories."""
    popular_category = filters.BooleanFilter(method='filter_popular_categories', label="Filter by Popular categories")
    new_category = filters.BooleanFilter(method='filter_new_categories', label="Filter by New categories")
    hits_category = filters.BooleanFilter(method='filter_hits_categories', label="Filter by Hits categories")
    is_available = filters.BooleanFilter(field_name='is_available')
    search = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = ProductCategories
        fields = ['is_popular', 'is_new', 'is_hit', 'is_available', 'search']

    def filter_popular_categories(self, queryset, name, value):
        """Filter queryset for popular categories."""
        if value:
            return queryset.filter(is_popular=True)[:15]
        return queryset

    def filter_new_categories(self, queryset, name, value):
        """Filter queryset for new categories."""
        if value:
            return queryset.filter(is_new=True)[:15]
        return queryset

    def filter_hits_categories(self, queryset, name, value):
        """Filter queryset for hit categories."""
        if value:
            return queryset.filter(is_hit=True)[:15]
        return queryset


class CategoryFilter(filters.NumberFilter):
    """Filter for product categories."""
    def filter(self, qs, value):
        """Filter queryset based on the selected category."""
        qs = qs.filter(
            Q(categoryId__id=value) |
            Q(categoryId__parent__id=value) |
            Q(categoryId__parent__parent__id=value)
        ) if value else qs
        return qs


class RemovePunctuation(Func):
    function = 'REPLACE'
    
    def __init__(self, expression, **extra):
        for mark in punctuation:
            expression = Replace(expression, Value(mark), Value(''))
        super().__init__(expression, **extra)

class ProductFilter(filters.FilterSet):
    """FilterSet for filtering products."""
    category_id = CategoryFilter(field_name='categoryId_id', lookup_expr='exact')
    search = filters.CharFilter(field_name='name', method='filter_search')
    material = filters.CharFilter(field_name='material', method='filter_material')
    brand = filters.CharFilter(field_name='brand', method='filter_brand')
    is_new = filters.BooleanFilter(field_name='is_new')
    is_hit = filters.BooleanFilter(field_name='is_hit')
    is_popular = filters.BooleanFilter(field_name='is_popular')
    is_available = filters.BooleanFilter(field_name='ondemand')
    warehouse = filters.CharFilter(field_name='warehouse', method='filter_warehouse')
    price = filters.CharFilter(field_name='price', method='filter_price')
    quantity = filters.CharFilter(field_name='quantity', method='filter_quantity')
    size = filters.CharFilter(field_name='size', method='filter_size')
    color = filters.CharFilter(method='filter_color')
    site = filters.CharFilter(field_name='site', lookup_expr='exact')

    @staticmethod
    def remove_punctuation(text):
        return text.translate(str.maketrans('', '', punctuation))

    def filter_search(self, queryset, name, value):
        value = self.remove_punctuation(value)
        queryset = queryset.annotate(clean_name=RemovePunctuation(F('name')))
        filtered_queryset = queryset.filter(clean_name__icontains=value)
        return filtered_queryset

    def filter_material(self, queryset, name, value):
        values = value.split(',')
        filtered_queryset = queryset.filter(material__in=values)
        return filtered_queryset

    def filter_brand(self, queryset, name, value):
        values = value.split(',')
        filtered_queryset = queryset.filter(brand__in=values)
        return filtered_queryset

    def filter_warehouse(self, queryset, name, value):
        if value == 'Европа':
            lookup = '__'.join([name, '1', 'quantity', 'gt'])
        elif value == 'Москва':
            lookup = '__'.join([name, '0', 'quantity', 'gt'])
        else:
            return Products.objects.none()
        filtered_queryset = queryset.filter(**{lookup: 0})
        return filtered_queryset

    def filter_price(self, queryset, name, value):
        if ',' not in value:
            filtered_queryset = queryset.filter(price__gte=value)
            return filtered_queryset
        start, end = map(int, value.split(','))
        filtered_queryset = queryset.filter(price__gte=start, price__lte=end)
        return filtered_queryset

    def filter_quantity(self, queryset, name, value):
        filtered_queryset = queryset.filter(warehouse__0__quantity__gte=int(value))
        return filtered_queryset

    def filter_size(self, queryset, name, value):
        filtered_queryset = queryset.filter(sizes__has_key=value)
        return filtered_queryset

    def filter_color(self, queryset, name, value):
        filtered_queryset = queryset.filter(images_set__colorID__name__icontains=value)
        return filtered_queryset

    class Meta:
        # model = Products
        fields = []
        # fields = ['category_id', 'search', 'brand', 'material', 'warehouse', 'is_new', 'is_hit', 'is_popular', 'is_available']
