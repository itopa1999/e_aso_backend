from rapidfuzz import fuzz
from django.db.models import Prefetch
from apps.aso.models import Product, LookUp

def smart_fuzzy_search_product_titles(query, limit=50):
    """
    AI-like fuzzy search across Product's title, description, badge, and category names.
    Returns a list of matching product titles ranked by relevance.
    """

    query = query.strip()
    if not query:
        return []

    # Prefetch categories to reduce DB hits
    products = Product.objects.prefetch_related(
        Prefetch('category', queryset=LookUp.objects.all())
    )

    results = []

    for product in products:
        # Combine all searchable fields
        category_names = " ".join([c.name for c in product.category.all()])
        text = f"{product.title} {product.description} {product.badge} {category_names}"

        # Compute multiple similarity scores
        token_set_score = fuzz.token_set_ratio(query, text)
        partial_score = fuzz.partial_ratio(query, text)
        simple_ratio = fuzz.ratio(query, text)

        # Final score is weighted max (tune weights if needed)
        score = max(token_set_score, partial_score, simple_ratio)

        # Lower threshold for very short queries
        effective_threshold = 10 if len(query) <= 3 else 50

        if score >= effective_threshold:
            results.append((product.title, score))

    # Sort by score descending
    results.sort(key=lambda x: x[1], reverse=True)

    # Deduplicate titles if any
    seen = set()
    unique_results = []
    for title, score in results:
        if title not in seen:
            unique_results.append((title, score))
            seen.add(title)

    # Return only the titles
    return [title for title, _ in unique_results[:limit]]
