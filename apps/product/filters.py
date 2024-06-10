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
        subcategories = ProductCategories.objects.filter(parent__isnull=False, parent__parent__isnull=True)
        return [(subcategory.id, subcategory.name) for subcategory in subcategories]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(parent_id=self.value())
        return queryset


class MainCategoryListFilter(SimpleListFilter):
    """Custom filter for main categories."""
    title = 'main category'
    parameter_name = 'main_category'

    def lookups(self, request, model_admin):
        main_categories = ProductCategories.objects.filter(parent__isnull=True)
        return [(cat.id, cat.name) for cat in main_categories]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(parent__id=self.value())
        return queryset


class ProductCategoryFilter(filters.FilterSet):
    """FilterSet for filtering product categories."""
    popular_category = filters.BooleanFilter(method='filter_popular_categories', label="Popular categories")
    new_category = filters.BooleanFilter(method='filter_new_categories', label="New categories")
    hits_category = filters.BooleanFilter(method='filter_hits_categories', label="Hits categories")
    is_available = filters.BooleanFilter(field_name='is_available')
    search = filters.CharFilter(field_name='name', lookup_expr='icontains')
    site = filters.CharFilter(field_name='site', lookup_expr='exact')

    class Meta:
        model = ProductCategories
        fields = ['is_popular', 'is_new', 'is_hit', 'is_available', 'search']

    @staticmethod
    def filter_popular_categories(queryset, _, value):
        if value:
            return queryset.filter(is_popular=True)[:15]
        return queryset

    @staticmethod
    def filter_new_categories(queryset, _, value):
        if value:
            return queryset.filter(is_new=True)[:15]
        return queryset

    @staticmethod
    def filter_hits_categories(queryset, _, value):
        if value:
            return queryset.filter(is_hit=True)[:15]
        return queryset


class CategoryFilter(filters.NumberFilter):
    """Filter for product categories."""
    def filter(self, qs, value):
        if value:
            subcategories = ProductCategories.objects.filter(
                Q(parent_id=value) | Q(parent__parent_id=value)
            ).values_list('id', flat=True)
            category_ids = list(subcategories) + [value]
            return qs.filter(categoryId__in=category_ids)
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
    gender = filters.CharFilter(method='filter_gender')
    print_type = filters.CharFilter(method='filter_print')
    site = filters.CharFilter(field_name='site', lookup_expr='exact')

    @staticmethod
    def remove_punctuation(text):
        return text.translate(str.maketrans('', '', '-,/'))

    def filter_search(self, queryset, _, value):
        value = self.remove_punctuation(value)
        queryset = queryset.annotate(
            name_no_comma=Replace(
                Replace(Replace(F('name'), Value('-'), Value('')), Value(','), Value('')), Value('/'), Value('')
            )
        )
        return queryset.filter(Q(name_no_comma__icontains=value))

    @staticmethod
    def filter_material(queryset, _, value):
        values = value.split(',')
        return queryset.filter(material__in=values)

    @staticmethod
    def filter_brand(queryset, _, value):
        values = value.split(',')
        return queryset.filter(brand__in=values)

    @staticmethod
    def filter_warehouse(queryset, _, value):
        if value == 'Европа':
            return queryset.filter(warehouse__1__quantity__gt=0)
        elif value == 'Москва':
            return queryset.filter(warehouse__0__quantity__gt=0)
        return Products.objects.none()

    @staticmethod
    def filter_price(queryset, _, value):
        if ',' in value:
            start, end = map(int, value.split(','))
            return queryset.filter(price__gte=start, price__lte=end)
        return queryset.filter(price__gte=value)

    @staticmethod
    def filter_quantity(queryset, _, value):
        return queryset.filter(warehouse__0__quantity__gte=int(value))

    @staticmethod
    def filter_size(queryset, _, value):
        return queryset.filter(sizes__has_key=value)

    @staticmethod
    def filter_color(queryset, _, value):
        return queryset.filter(colorID__name__icontains=value)

    @staticmethod
    def filter_gender(queryset, _, value):
        if value == 'male':
            return queryset.filter(name__icontains='мужс')
        elif value == 'female':
            return queryset.filter(name__icontains='женс')
        return queryset

    @staticmethod
    def filter_print(queryset, _, value):
        filtered_ids = [
            item.pk for item in queryset if any(
                print_item.get("@name") == 'Метод нанесения' and print_item.get("#text") == value
                for print_item in (item.prints if isinstance(item.prints, list) else [item.prints])
            )
        ]
        return queryset.filter(pk__in=filtered_ids)

    class Meta:
        model = Products
        fields = []
