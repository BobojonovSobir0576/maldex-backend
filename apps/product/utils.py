from apps.product.models import Products


def filter_by_sub_category(queryset, request):
    sub_category_id = request.query_params.get("sub_category")
    if not sub_category_id:
        return queryset

    try:
        sub_category_id = int(sub_category_id)
    except ValueError:
        return queryset.none()

    sub_category = queryset.filter(subcategory=sub_category_id).first()
    if not sub_category:
        return queryset.none()

    return Products.objects.select_related('categoryId').filter(categoryId__subcategory=sub_category)


def filter_by_category(queryset, request):
    category_id = request.query_params.get("category")
    if not category_id:
        return queryset

    try:
        category_id = int(category_id)
    except ValueError:
        return queryset.none()

    return Products.objects.select_related('categoryId').filter(categoryId=category_id)
