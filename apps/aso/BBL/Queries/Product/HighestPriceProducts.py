from http import HTTPStatus
from apps.aso.models import Product, CartItem
from utils.base_result import BaseResultWithData
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys


class HighestPriceProductsQuery:
    """Query to get top 15 products with highest current price"""
    
    @staticmethod
    def query(request):
        try:
            # Check cache first
            cache_key = CacheKeys.HIGHEST_PRICE_PRODUCTS.value
            cached_data = GlobalCache.get(cache_key)
            
            if cached_data:
                return BaseResultWithData(
                    data=cached_data,
                    status_code=HTTPStatus.OK,
                    message="Success"
                )
            
            # Get top 15 products ordered by current_price descending
            products = Product.objects.filter(
                display_product=True,
                is_deleted=False,
                current_price__isnull=False
            ).order_by('-current_price')[:15]
            
            if not products:
                return BaseResultWithData(
                    data=[],
                    status_code=HTTPStatus.OK,
                    message="No products found"
                )
            
            # Format response data
            products_data = []
            for product in products:
                # Get product images
                product_images = product.images.filter(is_deleted=False)
                images_list = []
                if request:
                    for img_obj in product_images:
                        if img_obj.image and hasattr(img_obj.image, 'url'):
                            images_list.append(request.build_absolute_uri(img_obj.image.url))
                else:
                    for img_obj in product_images:
                        if img_obj.image:
                            images_list.append(f"/media/{img_obj.image.name}")
                
                # Get main image
                main_image = None
                if product.main_image:
                    if request and hasattr(product.main_image, 'url'):
                        main_image = request.build_absolute_uri(product.main_image.url)
                    else:
                        main_image = f"/media/{product.main_image.name}" if product.main_image else None
                
                # Calculate discount
                discount = product.discount_percent or 0
                
                # Check if product is in user's cart
                cart_added = False
                if request and request.user and request.user.is_authenticated:
                    cart_added = CartItem.objects.filter(
                        cart__user=request.user,
                        product=product,
                        is_deleted=False
                    ).exists()
                
                products_data.append({
                    "id": product.id,
                    "title": product.title,
                    "description": product.description,
                    "original_price": float(product.original_price),
                    "current_price": float(product.current_price or 0),
                    "discount": discount,
                    "product_main_image": main_image,
                    "product_images": images_list,
                    "cart_added": cart_added,
                })
                
            # Cache the data
            GlobalCache.set(cache_key, products_data)
            
            return BaseResultWithData(
                data=products_data,
                status_code=HTTPStatus.OK,
                message="Success"
            )
            
            
            
        except Exception as e:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="Error retrieving products"
            )
