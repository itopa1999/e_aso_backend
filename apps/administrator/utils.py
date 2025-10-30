

def apply_date_category_filters(queryset, request):
    """
    Applies date range and category filters dynamically.
    ?start_date=2025-10-01&end_date=2025-10-29&category=Men
    """
    start_date = request.query_params.get("start_date")
    end_date = request.query_params.get("end_date")
    category = request.query_params.get("category")

    if start_date:
        queryset = queryset.filter(created_at__date__gte=start_date)
    if end_date:
        queryset = queryset.filter(created_at__date__lte=end_date)
    if category:
        queryset = queryset.filter(items__product__category__name__icontains=category)

    return queryset
