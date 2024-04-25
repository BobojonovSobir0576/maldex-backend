from apps.product.models import Products


def filter_by_sub_category(queryset, request):
    """
    Filter products by subcategory ID.
    """
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
    """
    Filter products by category ID.
    """
    category_id = request.query_params.get("category")
    if not category_id:
        return queryset

    try:
        category_id = int(category_id)
    except ValueError:
        return queryset.none()

    return Products.objects.select_related('categoryId').filter(categoryId=category_id)


def get_subcategories(queryset, request):
    """
    Get subcategories.
    """
    cate_id = request.query_params.get("sub_category")
    if not cate_id:
        return queryset

    try:
        cate_id = int(cate_id)
    except ValueError:
        return queryset.none()

    return queryset.filter(subcategory=cate_id)


def get_tertiary_category(queryset, request):
    """
    Get tertiary categories.
    """
    tertiary_category = request.query_params.get('tertiary_category')
    if not tertiary_category:
        return queryset

    try:
        tertiary_category = int(tertiary_category)
    except ValueError:
        return queryset.none()

    return queryset.filter(tertiary_category=tertiary_category)


def get_popular_categories(queryset, request):
    """
    Get popular categories.
    """
    is_popular = request.query_params.get('popular_category', False)
    if not is_popular:
        return queryset
    return queryset.filter(is_popular=True)[0:15]
