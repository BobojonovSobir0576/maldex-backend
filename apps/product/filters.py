from django.contrib.admin import SimpleListFilter
from apps.product.models import ProductCategories, Products
from django_filters import rest_framework as filters


class SubCategoryListFilter(SimpleListFilter):
    title = 'subcategory'

    parameter_name = 'subcategory'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each tuple is the coded value for the option that will
        appear in the URL query. The second element is the human-readable name for the option that will appear
        in the right sidebar.
        """
        subcategories = ProductCategories.objects.filter(parent__isnull=False, parent__parent__isnull=True)
        return [(subcategory.id, subcategory.name) for subcategory in subcategories]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(parent_id=self.value())
        return queryset


class MainCategoryListFilter(SimpleListFilter):
    title = 'main category'
    parameter_name = 'main_category'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each tuple is the coded value for the option that will
        appear in the URL query. The second element is the human-readable name for the option that will appear
        in the right sidebar.
        """
        main_categories = ProductCategories.objects.filter(parent__isnull=True)
        return [(cat.id, cat.name) for cat in main_categories]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(parent__id=self.value())
        return queryset


class ProductCategoryFilter(filters.FilterSet):
    popular_category = filters.BooleanFilter(method='filter_popular_categories', label="Filter by Popular categories")
    new_category = filters.BooleanFilter(method='filter_new_categories', label="Filter by New categories")  # Corrected method name
    hits_category = filters.BooleanFilter(method='filter_hits_categories', label="Filter by Hits categories")  # Corrected method name

    class Meta:
        model = ProductCategories
        fields = ['is_popular', 'is_new', 'is_hit']

    def filter_popular_categories(self, queryset, value):
        if value:
            return queryset.filter(is_popular=True)[:15]
        return queryset

    def filter_new_categories(self, queryset, value):
        if value:
            return queryset.filter(is_new=True)[:15]
        return queryset

    def filter_hits_categories(self, queryset, value):
        if value:
            return queryset.filter(is_hit=True)[:15]
        return queryset


class ProductFilter(filters.FilterSet):
    category = filters.UUIDFilter(field_name='categoryId__id', lookup_expr='exact')

    class Meta:
        model = Products
        fields = ['categoryId']