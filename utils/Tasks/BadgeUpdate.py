from django.db.models import Count

from apps.aso.models import OrderItem, Product

def update_best_selling_products(threshold=4):
    """
    Scan all OrderItems and mark products as 'Best Seller' 
    if they appear in orders at least `threshold` times.
    """
    # 1️⃣ Aggregate counts of each product across all order items
    product_sales = (
        OrderItem.objects
        .values('product')
        .annotate(total_sold=Count('id'))
        .filter(total_sold__gte=threshold)
    )

    best_selling_ids = [item['product'] for item in product_sales]

    updated = Product.objects.filter(id__in=best_selling_ids).update(badge="Best Seller")

    Product.objects.exclude(id__in=best_selling_ids).filter(badge="Best Seller").update(badge="New")

    print(f"✅ Updated {updated} products to 'Best Seller'.")
