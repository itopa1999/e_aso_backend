from http import HTTPStatus
from apps.aso.models import Product
from utils.base_result import BaseResultWithData
from utils.cache_manager import GlobalCache
from utils.enum import CacheKeys


class ProductDetailQuery:
    @staticmethod
    def query(product_id):
        cache_key = CacheKeys.format(CacheKeys.PRODUCT_DETAIL, product_id=product_id)

        cached_data = GlobalCache.get(cache_key)
        if cached_data:
            return BaseResultWithData(
                data=cached_data["data"],
                status_code=HTTPStatus.OK,
                message="Product detail fetched successfully."
            )
        try:
            product = Product.objects.filter(
                id=product_id, display_product=True, is_deleted=False
            ).first()

            if not product:
                return BaseResultWithData(
                    data=None,
                    status_code=HTTPStatus.NOT_FOUND,
                    message="Product not found."
                )

            # Increment views/reviews count
            product.reviews_count = (product.reviews_count or 0) + 1
            product.save(update_fields=["reviews_count"])
            
            GlobalCache.set(cache_key, {"data": product})

            return BaseResultWithData(
                data=product,
                status_code=HTTPStatus.OK,
                message="Product detail retrieved successfully."
            )

        except Exception as e:
            return BaseResultWithData(
                data=None,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Failed to retrieve product: {str(e)}"
            )
