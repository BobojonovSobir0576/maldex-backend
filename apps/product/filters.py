from django.contrib.admin import SimpleListFilter
from django.db.models import Q
from django_filters import rest_framework as filters
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
        )
        return qs


class ProductFilter(filters.FilterSet):
    """FilterSet for filtering products."""
    category_id = CategoryFilter(field_name='categoryId_id')
    search = filters.CharFilter(field_name='name', lookup_expr='icontains')
    material = filters.CharFilter(field_name='material', lookup_expr='icontains')
    brand = filters.CharFilter(field_name='brand', lookup_expr='icontains')
    is_new = filters.BooleanFilter(field_name='is_new')
    is_hit = filters.BooleanFilter(field_name='is_hit')
    is_popular = filters.BooleanFilter(field_name='is_popular')
    is_available = filters.BooleanFilter(field_name='ondemand')
    warehouse = filters.CharFilter(field_name='warehouse', method='filter_warehouse')
    price = filters.CharFilter(field_name='price', method='filter_price')
    quantity = filters.CharFilter(field_name='quantity', method='filter_quantity')

    def filter_warehouse(self, queryset, name, value):
        if value == 'Европа':
            lookup = '__'.join([name, '0', 'quantity', 'gt'])
        elif value == 'Москва':
            lookup = '__'.join([name, '1', 'quantity', 'gt'])
        else:
            return Products.objects.none()
        print(lookup)
        return queryset.filter(**{lookup: 0})

    def filter_price(self, queryset, name, value):
        if ',' not in value:
            return queryset.filter(price__gte=value)
        start, end = map(int, value.split(','))
        print(start, end)
        return queryset.filter(price__gte=start, price__lte=end)

    def filter_quantity(self, queryset, name, value):
        return queryset.filter(warehouse__0__quantity__gte=int(value))

    class Meta:
        model = Products
        fields = ['category_id', 'search', 'brand', 'material', 'warehouse', 'is_new', 'is_hit', 'is_popular', 'is_available']
