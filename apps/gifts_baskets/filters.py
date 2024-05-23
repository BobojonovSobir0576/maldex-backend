from django_filters import rest_framework as filters
from apps.gifts_baskets.models import *


class GiftsBasketCategoryProductFilter(filters.FilterSet):
    sub_catalog = filters.NumberFilter(method='get_sub_catalog', label='Get sub catalog')

    class Meta:
        model = GiftsBasketCategory
        fields = ['parent']

    @staticmethod
    def get_sub_catalog(queryset, name, value):
        if value:
            return queryset.filter(parent=value)
        return queryset
